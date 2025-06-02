import os
import json
import tempfile
from typing import List, Dict, Optional
from label_studio_ml.model import LabelStudioMLBase
from label_studio_ml.utils import get_image_size, \
    get_single_tag_keys, DATA_UNDEFINED_NAME

import cv2
import numpy as np

class NewModel(LabelStudioMLBase):
    def __init__(self, config_file=None,
                 checkpoint_file=None,
                 image_dir=None,
                 labels_file=None, score_threshold=0.3, device='cpu', **kwargs):
                     
        super(NewModel, self).__init__(**kwargs)
        
        self.model_dir = '.'
        self.hostname = os.environ['LABEL_STUDIO_HOST']
        self.access_token = os.environ['LABEL_STUDIO_API_KEY']
        self.score_thresh = score_threshold
        
        model_version = 'contour-detector'
        
        try:
            filename=tempfile.gettempdir()+'/'+model_version+'.json'
            with open(filename, 'r') as openfile:
                # Reading from json file
                default_label = json.load(openfile)
        except:
            default_label = 'coin'
        
        try:
            self.set('model_version', model_version)
            self.set('my_data', default_label)
            
            if not self.get('label_config'):
                self.set('label_config',"{}")
            
            if not self.get('parsed_label_config'):
                self.set('parsed_label_config',"{}")
        except:
            self.model_version = model_version
            self.my_data = default_label
            
            if not self.label_config:
                self.label_config={}   
            
            if not self.parsed_label_config:
                self.parsed_label_config={}   
        
        # print("!!!breakpoint!!!")
        # breakpoint() 
        
        if len(self.parsed_label_config)==1:
            self.from_name, self.to_name, self.value, self.labels_in_config = get_single_tag_keys(
                self.parsed_label_config, 'RectangleLabels', 'Image')
            # schema = list(self.parsed_label_config.values())[0]
            self.labels_in_config = set(self.labels_in_config)

        # print("=====")
        # print("self.labels_in_config:",self.labels_in_config)
        # print("=====")
                     
    def predict(self, tasks: List[Dict], context: Optional[Dict] = None, **kwargs) -> List[Dict]:
        """ Write your inference logic here
            :param tasks: [Label Studio tasks in JSON format](https://labelstud.io/guide/task_format.html)
            :param context: [Label Studio context in JSON format](https://labelstud.io/guide/ml.html#Passing-data-to-ML-backend)
            :return predictions: [Predictions array in JSON format](https://labelstud.io/guide/export.html#Raw-JSON-format-of-completed-tasks)
        """
        # Hostname is {self.hostname}
        # Run prediction on {tasks}
        # Received context: {context}
        # Project ID: {self.project_id}
        # Label config: {self.label_config}
        # Parsed JSON Label config: {self.parsed_label_config}
        # return []
        
        # print("!!!breakpoint!!!")
        # breakpoint()
        
        assert len(tasks) == 1
        task = tasks[0]
        image_url = self.hostname+self._get_image_url(task)
        image_path = self.get_local_path(image_url)
        # print("image_path:",image_path)
        
        # print(f'''\
        # Run prediction on {image_path}
        # Label config: {self.labels_in_config}
        # ''')
        
        # model_results = self.bbox_detector(image_path, self.labels_in_config)
        model_results = self.bbox_detector_iou_area(image_path)
        
        results = []
        all_scores = []
        img_width, img_height = get_image_size(image_path)
        
        for item in model_results:
            bboxes, output_label, scores = item['bboxes'], item['labels'][0], item['scores']

            for bbox in bboxes:
                bbox = list(bbox)
                if not bbox:
                    # print("not bbox")
                    logger.info("not bbox")
                    continue
                # score = float(bbox[-1])
                score = float(scores.pop(0))
                if score < self.score_thresh:
                    continue
                x, y, width, height = [float(i) for i in bbox]
                results.append({
                    'from_name': self.from_name,
                    'to_name': self.to_name,
                    'type': 'rectanglelabels',
                    'value': {
                        'rectanglelabels': [output_label],
                        'x': x / img_width * 100,
                        'y': y / img_height * 100,
                        'width': width / img_width * 100,
                        'height': height / img_height * 100
                    },
                    'score': score
                })
                all_scores.append(score)
        avg_score = sum(all_scores) / max(len(all_scores), 1)
        # print("=====")
        # print("results:",results)
        # print("avg_score:",avg_score)
        # print("=====")
        return [{
            'result': results,
            'score': avg_score
        }]

    def fit(self, event, data, **kwargs):
        """
        This method is called each time an annotation is created or updated
        You can run your logic here to update the model and persist it to the cache
        It is not recommended to perform long-running operations here, as it will block the main thread
        Instead, consider running a separate process or a thread (like RQ worker) to perform the training
        :param event: event type can be ('ANNOTATION_CREATED', 'ANNOTATION_UPDATED')
        :param data: the payload received from the event (check [Webhook event reference](https://labelstud.io/guide/webhook_reference.html))
        """

        # use cache to retrieve the data from the previous fit() runs
        try:
            old_model_version = self.get('model_version')
            old_data = self.get('my_data')
        except:
            old_model_version = self.model_version
            old_data = self.my_data
            
        print(f'Old model version: {old_model_version}')
        print(f'Old data: {old_data}')

        # print("!!!breakpoint!!!")
        # breakpoint()
        
        # store new data to the cache
        # model_version = None
        # my_data = None
        # self.set('my_data', 'my_new_data_value')
        # self.set('model_version', 'my_new_model_version')
        try:
            model_version = data['project']['model_version']
            if model_version: self.set('model_version', model_version)
        except:
            pass
            
        try:
            my_data = data['project']['my_data']
            if my_data: 
                self.set('my_data', my_data)
                
                filename=tempfile.gettempdir()+'/'+old_model_version+'.json'
                with open(filename, "w") as outfile:
                    outfile.write(json.dumps(my_data, indent=4))
        except:
            pass
            
        try:
            print(f'New model version: {self.get("model_version")}')
            print(f'New data: {self.get("my_data")}')
        except:
            print(f'New model version: {self.model_version}')
            print(f'New data: {self.my_data}')

        print('fit() completed successfully.')

        if event.startswith('ANNOTATION_UPDATED'):
            # print("=====")
            # print("data:",data)
            # print("=====")
            self.set('last_annotation', json.dumps(data['annotation']['result']))
        elif event.startswith('PROJECT_UPDATED'):
            # print("=====")
            # print("data:",data)
            # print("=====")
            self.set('last_project', json.dumps(data['project']))

    def _get_image_url(self, task):
        image_url = task['data'].get(self.value) or task['data'].get(DATA_UNDEFINED_NAME)
        if image_url.startswith('s3://'):
            # presign s3 url
            r = urlparse(image_url, allow_fragments=False)
            bucket_name = r.netloc
            key = r.path.lstrip('/')
            client = boto3.client('s3', endpoint_url=self.endpoint_url)
            try:
                image_url = client.generate_presigned_url(
                    ClientMethod='get_object',
                    Params={'Bucket': bucket_name, 'Key': key}
                )
            except ClientError as exc:
                logger.warning(f'Can\'t generate presigned URL for {image_url}. Reason: {exc}')
        return image_url

        
    def bbox_detector(self, image_path, labels):
        
        # print("!!!breakpoint!!!")
        # breakpoint()
        
        import cv2 as cv
        img = cv.imread(image_path, cv.IMREAD_GRAYSCALE)
        assert img is not None, "file could not be read, check with os.path.exists()"
        ret,thresh = cv.threshold(img,127,255,0)
        # contours,hierarchys = cv.findContours(thresh, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        contours,hierarchys = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        
        from enum import Enum
        class Hierarchy(Enum):
            Next     = 0
            Previous    = 1
            First_Child  = 2
            Parent   = 3
    
        def find_parent(hierarchy, index):
            # print("index:",index)
            # print("hierarchy[index]:",hierarchy[index])
            if hierarchy[index][Hierarchy.Parent.value] == -1:
                return index
                # return hierarchy[index][2]
            else:
                return find_parent(hierarchy, hierarchy[index][Hierarchy.Parent.value])
        
        results = []

        for hierarchy in hierarchys:
            headi = find_parent(hierarchy,0) 
            childi = hierarchy[headi][Hierarchy.First_Child.value]
            
            while childi != -1:
                item = {}
                bboxes = []
                outlabels = []
                scores = []
                
                cnt = contours[childi]
                x,y,w,h = cv.boundingRect(cnt)
                bbox = [x,y,w,h]
                bboxes.append(bbox)
                # outlabels.append(labels.pop())
                # outlabels.append('coin')
                try:
                    outlabels.append(self.get('my_data')) #guess a label
                except:
                    outlabels.append(self.my_data) #guess a label
                scores.append(100.0)
                
                childi = hierarchy[childi][Hierarchy.Next.value]
        
                item['bboxes'] = bboxes
                item['labels'] = outlabels
                item['scores'] = scores
                results.append(item)
        
        return results


    def bbox_detector_iou_area(self, image_path):
        from bbox_detector import get_marker_corners, get_paper_corners, get_corners_bounding_box, get_mask, get_contours_tree, get_corners_area

        # print(f"bbox_detector_iou_area| processing file {image_path}")

        raw_image = cv2.imread(image_path)

        # image=undistort(raw_image)
        image=raw_image.copy()

        corners, ids = get_marker_corners(image)
        if len(corners) == 0:
            image=raw_image.copy()
            corners, ids = get_marker_corners(image)

        # image2=image.copy()
        # image3=image.copy()
        # image4=image.copy()
        # image5=image.copy()

        results = []

        if len(corners) > 0:
            ids = ids.flatten()
            for markerCorner, markerID in zip(corners, ids):
                corners = markerCorner.reshape((4, 2))
                # (topLeft, topRight, bottomRight, bottomLeft) = corners

                paper_corners = get_paper_corners(corners, image.shape)
                paper_dimensions = get_corners_bounding_box(paper_corners)
        
                mask_img = get_mask(image.shape, np.array(paper_corners).astype(int))
                mask_img = cv2.cvtColor(mask_img, cv2.COLOR_BGR2GRAY)
                # show_image(mask_img, f"ID {markerID} mask", 720)

                paper_img = cv2.bitwise_and(image, image, mask=mask_img)
                # show_image(paper_img, f"ID {markerID} paper_img", 720)

                contours, hierarchys, hasParents = get_contours_tree(paper_img)

                area = get_corners_area(corners)
                
                self.detect_contours_by_iou_minum_area(results, paper_dimensions, contours, 0.7, area)

        else:
            paper_img = image.copy()
            paper_dimensions = (0, 0, paper_img.shape[1], paper_img.shape[0])

            # contours, hierarchys, hasParents = get_contours_onpaper(paper_img)
            contours, hierarchys, hasParents = get_contours_tree(paper_img)

            area = paper_img.shape[0] * paper_img.shape[1] / 4
            
            self.detect_contours_by_iou_minum_area(results, paper_dimensions, contours, 0.7, area)
        
        return results

    def detect_contours_by_iou_minum_area(self, results, paper_dimensions, contours, iou_threshold=0.7, min_area=100):
        from bbox_detector import find_parent_by_iou

        # print(f"draw_contours_by_iou_minum_area| paper_dimensions: {paper_dimensions}")
        cons = []
        # papar_width = img.shape[1]
        # papar_height = img.shape[0]
        for i in range(len(contours)):
            cnt = contours[i]
            x, y, w, h = cv2.boundingRect(cnt)
            w_ratio = w / paper_dimensions[2]
            h_ratio = h / paper_dimensions[3]
            area = cv2.contourArea(cnt)
            area_ratio = area / min_area
            # print(f"draw_contours_by_iou: Contour {i}, bounding box: ({x}, {y}, {w}, {h}), ratio: {w/paper_dimensions[2]:.02f} {h/paper_dimensions[3]:.02f}")
            if h_ratio < 0.85 and w_ratio < 0.85 and area_ratio > 0.145:
                cons.append(cnt)

        contours = cons
        # for i in range(len(contours)):
        #     cnt = contours[i]
        #     x, y, w, h = cv2.boundingRect(cnt)
        #     print(f"draw_contours_by_iou: Contour {i}, bounding box: ({x}, {y}, {w}, {h})")

        # 找出父輪廓
        parent_indices = find_parent_by_iou(contours, iou_threshold)
        # print(f"draw_contours_by_iou| Found {len(parent_indices)} parent contours with IOU threshold {iou_threshold}")
        # print(f"parent_indices {parent_indices}")

        # results = []
        # 繪製父輪廓
        for id in parent_indices:
            cnt = contours[id]
            x, y, w, h = cv2.boundingRect(cnt)
            # cv2.rectangle(img, (x, y), (x + w, y + h), red, 2)
            
            # 顯示輪廓資訊
            area = cv2.contourArea(cnt)
            area_ratio = area / min_area

            # cv2.putText(img, f"{id}:{area:.0f}", (x+1, y - 10+1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, white, 2)
            # cv2.putText(img, f"{id}:{area:.0f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, blue, 2)
            # draw_label(img, f"{id}:{area_ratio:.02f}", x, y-10, color=blue)

            # print(f"draw_contours_by_iou_minum_area| Contour {id}, area_ratio {area_ratio:.03f}, bounding box: ({x}, {y}, {w}, {h})")

            item = {}
            bboxes = []
            outlabels = []
            scores = []
            
            # cnt = contours[childi]
            x,y,w,h = cv2.boundingRect(cnt)
            bbox = [x,y,w,h]
            bboxes.append(bbox)
            # outlabels.append(labels.pop())
            # outlabels.append('coin')
            try:
                outlabels.append(self.get('my_data')) #guess a label
            except:
                outlabels.append(self.my_data) #guess a label
            scores.append(100.0)
            
            # childi = hierarchy[childi][Hierarchy.Next.value]
    
            item['bboxes'] = bboxes
            item['labels'] = outlabels
            item['scores'] = scores
            results.append(item)
        
        # show_image(img, f'draw_contours_by_iou_minum_area (threshold={iou_threshold} min_area={min_area:.0f})', 720)

        # return results


def main():
    model = NewModel()
    model.bbox_detector_iou_area('data/images/coin.png')
    model.bbox_detector_iou_area('data/images/3c115d9c-8839-4ae8-9f3f-96d514dd5831.png')
    model.bbox_detector_iou_area('data/images/482585764_1455590368759521_6647519779772489171_n.png')

if __name__ == "__main__":
    main()
