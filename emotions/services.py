"""
表情识别与人脸识别服务
"""
import os
import cv2
import numpy as np
from django.conf import settings


class FaceRecognitionService:
    """人脸识别服务"""
    
    def __init__(self):
        self.model_path = settings.FACE_MODEL_PATH
        self.threshold = settings.FACE_MATCH_THRESHOLD
        self.db_path = os.path.join(settings.MEDIA_ROOT, 'faces_db')
        os.makedirs(self.db_path, exist_ok=True)
        
        # 尝试加载模型
        try:
            import tensorflow as tf
            self.interpreter = tf.lite.Interpreter(model_path=str(self.model_path))
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()[0]
            self.output_details = self.interpreter.get_output_details()[0]
            self.model_loaded = True
        except Exception as e:
            print(f"[WARNING] 人脸识别模型加载失败: {e}")
            self.model_loaded = False
    
    def embed(self, face_image):
        """
        提取人脸特征向量
        
        Args:
            face_image: BGR格式的人脸图像(numpy array)
        
        Returns:
            特征向量(numpy array)
        """
        if not self.model_loaded:
            raise ValueError("人脸识别模型未加载")
        
        # 预处理
        face = cv2.resize(face_image, (112, 112))
        face = face.astype(np.float32) / 255.0
        face = np.expand_dims(face, 0)
        
        # 推理
        self.interpreter.set_tensor(self.input_details['index'], face)
        self.interpreter.invoke()
        embedding = self.interpreter.get_tensor(self.output_details['index'])[0]
        
        return embedding.copy()
    
    def register_face(self, user, face_image, photo_path):
        """
        注册用户人脸
        
        Args:
            user: User对象
            face_image: 人脸图像
            photo_path: 照片保存路径
        
        Returns:
            特征向量
        """
        from emotions.models import FaceEncoding
        
        # 提取特征
        embedding = self.embed(face_image)
        
        # 保存到数据库
        face_encoding = FaceEncoding.objects.create(
            user=user,
            encoding_vector=embedding.tobytes(),
            encoding_json=embedding.tolist(),
            photo_path=photo_path,
            is_primary=(user.face_encodings.count() == 0)
        )
        
        # 更新用户状态
        user.face_registered = True
        user.face_encodings_count = user.face_encodings.count()
        user.save()
        
        return embedding
    
    def recognize(self, face_image):
        """
        识别人脸
        
        Args:
            face_image: 人脸图像
        
        Returns:
            (user, distance) 或 (None, distance)
        """
        from emotions.models import FaceEncoding
        from users.models import User
        
        # 提取特征
        query_embedding = self.embed(face_image)
        
        # 获取所有用户特征
        face_encodings = FaceEncoding.objects.select_related('user').filter(
            user__face_registered=True,
            user__status='active'
        )
        
        if not face_encodings:
            return None, 1.0
        
        # 计算距离
        best_match = None
        min_distance = float('inf')
        
        for face_enc in face_encodings:
            stored_embedding = np.frombuffer(face_enc.encoding_vector, dtype=np.float32)
            distance = np.linalg.norm(stored_embedding - query_embedding)
            
            if distance < min_distance:
                min_distance = distance
                best_match = face_enc.user
        
        # 判断是否匹配
        if min_distance < self.threshold:
            return best_match, min_distance
        else:
            return None, min_distance


class EmotionRecognitionService:
    """表情识别服务"""
    
    EMOTIONS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
    EMOTIONS_CN = ["愤怒", "厌恶", "恐惧", "快乐", "悲伤", "惊讶", "中性"]
    
    def __init__(self):
        self.model_path = settings.EMOTION_MODEL_PATH
        self.threshold = settings.EMOTION_CONFIDENCE_THRESHOLD
        
        # 加载模型
        try:
            import tensorflow as tf
            self.model = tf.keras.models.load_model(str(self.model_path))
            self.model_loaded = True
        except Exception as e:
            print(f"[WARNING] 表情识别模型加载失败: {e}")
            self.model_loaded = False
    
    def detect_emotion(self, face_image):
        """
        检测表情
        
        Args:
            face_image: 灰度人脸图像(48x48)
        
        Returns:
            dict: {
                'emotion': 主要表情,
                'emotion_cn': 中文名称,
                'confidence': 置信度,
                'probabilities': 所有表情概率
            }
        """
        if not self.model_loaded:
            raise ValueError("表情识别模型未加载")
        
        # 预处理
        if len(face_image.shape) == 3:
            face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        
        face_image = cv2.resize(face_image, (48, 48))
        face_image = face_image.astype('float32') / 255.0
        face_image = np.expand_dims(face_image, axis=0)
        face_image = np.expand_dims(face_image, axis=-1)
        
        # 预测
        predictions = self.model.predict(face_image, verbose=0)[0]
        emotion_idx = np.argmax(predictions)
        confidence = float(predictions[emotion_idx])
        
        # 构造结果
        result = {
            'emotion': self.EMOTIONS[emotion_idx],
            'emotion_cn': self.EMOTIONS_CN[emotion_idx],
            'confidence': confidence,
            'probabilities': {
                self.EMOTIONS[i]: {
                    'name_cn': self.EMOTIONS_CN[i],
                    'value': float(predictions[i])
                }
                for i in range(len(self.EMOTIONS))
            },
            'ai_analysis': self._generate_analysis(self.EMOTIONS[emotion_idx], confidence)
        }
        
        return result
    
    def _generate_analysis(self, emotion, confidence):
        """生成AI分析文本"""
        analyses = {
            'happy': f'您看起来心情愉悦,继续保持这种状态!置信度{confidence:.1%}',
            'neutral': f'您的表情比较平静,这是一种稳定的情绪状态。置信度{confidence:.1%}',
            'sad': f'检测到您可能有些沮丧,建议找亲友倾诉或做些喜欢的事情。置信度{confidence:.1%}',
            'angry': f'您似乎有些生气,建议深呼吸放松,避免情绪失控。置信度{confidence:.1%}',
            'fear': f'检测到您可能有些紧张或焦虑,建议适当休息调整。置信度{confidence:.1%}',
            'surprise': f'您看起来有些惊讶,这可能是遇到了意外的事情。置信度{confidence:.1%}',
            'disgust': f'您似乎对某事感到厌恶,建议暂时远离不适的环境。置信度{confidence:.1%}',
        }
        return analyses.get(emotion, f'表情识别完成,置信度{confidence:.1%}')


# 全局单例
face_recognition_service = FaceRecognitionService()
emotion_recognition_service = EmotionRecognitionService()