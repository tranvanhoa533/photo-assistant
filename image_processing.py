import imagehash
from multiprocessing import Process, Value
from database.tabledef import UserImage
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine, Date
import nmslib
import multiprocessing
from flask import session
engine = create_engine('sqlite:///ap.db', echo=True)

class ImageProcessing(Process):

    def __init__(self, image_queue):
        super().__init__()
        self.image_queue = image_queue
        

    def run(self):

        Session = scoped_session(sessionmaker(bind=engine))
        sess = Session()

        while True:
            id, im = self.image_queue.get()
            hash_raw = imagehash.phash(im).hash.flatten()
            hash_str = ' '.join([str(int(item)) for item in hash_raw])
            query = sess.query(UserImage).filter(UserImage.id.in_((id,)))
            user_img = query.first()
            user_img.imghash = hash_str
            sess.add(user_img)
            sess.commit()   
            print(hash_str)

    def image_clustering(self):
        Session = scoped_session(sessionmaker(bind=engine))
        sess = Session()
        query = sess.query(UserImage).filter(UserImage.userid.in_([session['user_id']]))
        result = query.all()

        user_img_hash = []
        for user_img in result:
            user_img_hash.append(user_img.imghash)

        index = nmslib.init(method='hnsw', 
                            space='bit_hamming', 
                            dtype=nmslib.DistType.INT, 
                            data_type=nmslib.DataType.OBJECT_AS_STRING)

        index.addDataPointBatch(user_img_hash)
        index.createIndex({'post': 2}, print_progress=True)

        k = min(100, len(result))
        num_threads = multiprocessing.cpu_count()
        neighbours = index.knnQueryBatch(user_img_hash, k=k, num_threads=num_threads)

        threshold = 5
        similar = {}
        for i, item in enumerate(neighbours):
            similar[i] = []
            ids, distances = item
            for id, distance in zip(ids, distances):
                if distance <= threshold:
                    if i != id:
                        similar[i].append(id)
                else:
                    break

        groups = [None]*len(result)
        cur_group_id = 0
        for im_id in range(len(result)):
            if groups[im_id] is None:
                groups[im_id] = cur_group_id
                cur_group_id += 1

            for child_im_id in similar[im_id]:
                if groups[child_im_id] is None:
                    groups[child_im_id] = groups[im_id]

        for user_img, group in zip(result, groups):
            user_img.groupid = group
            sess.add(user_img)
        sess.commit()
        
        

def start_process(image_queue):
    process = ImageProcessing(image_queue)
    process.daemon = True
    process.start()

    return process

