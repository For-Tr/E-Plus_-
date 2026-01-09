"""
用户REST API视图（给鸿蒙App使用）
"""
import os
import base64
from django.contrib.auth import authenticate
from django.core.files.base import ContentFile
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from users.models import User
from families.models import InviteCode
from emotions.services import face_recognition_service
from emotions.models import FaceEncoding


class LoginAPIView(APIView):
    """用户登录API"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': '用户名和密码不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 认证用户
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response({
                'error': '用户名或密码错误'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.status != 'active':
            return Response({
                'error': '账户已被停用'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 更新最后登录时间
        user.last_login = timezone.now()
        user.save()
        
        # 生成JWT Token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'display_name': user.display_name,
                'email': user.email,
                'role': user.role,
                'face_registered': user.face_registered,
                'family': {
                    'id': user.family.id,
                    'name': user.family.family_name
                } if user.family else None
            }
        }, status=status.HTTP_200_OK)


class InviteCodeLoginAPIView(APIView):
    """邀请码直接登录API（无需账号密码）"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        invite_code = request.data.get('invite_code')
        
        if not invite_code:
            return Response({
                'error': '邀请码不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证邀请码
        try:
            invite = InviteCode.objects.select_related('family', 'created_by', 'used_by').get(code=invite_code)
        except InviteCode.DoesNotExist:
            return Response({
                'error': '邀请码不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 检查邀请码是否已使用(已关联用户)
        if not invite.used_by:
            return Response({
                'error': '邀请码尚未激活,请联系管理员'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查邀请码是否过期
        if invite.expires_at and timezone.now() > invite.expires_at:
            return Response({
                'error': '邀请码已过期'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = invite.used_by
        
        # 检查用户状态
        if user.status != 'active':
            return Response({
                'error': '账户已被停用'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 更新最后登录时间
        user.last_login = timezone.now()
        user.save()
        
        # 生成JWT Token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'display_name': user.display_name,
                'email': user.email,
                'role': user.role,
                'face_registered': user.face_registered,
                'family': {
                    'id': user.family.id,
                    'name': user.family.family_name
                } if user.family else None
            },
            'invite_code': invite_code  # 返回邀请码供后续使用
        }, status=status.HTTP_200_OK)


class RegisterAPIView(APIView):
    """用户注册API（已废弃,改用邀请码直接登录）"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        return Response({
            'error': '此API已废弃,请使用邀请码直接登录: POST /api/v1/auth/invite-login/'
        }, status=status.HTTP_410_GONE)
        
        return Response({
            'message': '注册成功',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'display_name': user.display_name,
                'role': user.role,
                'face_registered': user.face_registered,
                'family': {
                    'id': user.family.id,
                    'name': user.family.family_name
                }
            }
        }, status=status.HTTP_201_CREATED)


class LogoutAPIView(APIView):
    """用户登出API"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({
                'message': '登出成功'
            }, status=status.HTTP_200_OK)
        except Exception:
            return Response({
                'error': '登出失败'
            }, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserAPIView(APIView):
    """获取当前用户信息"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'display_name': user.display_name,
            'email': user.email,
            'phone': user.phone,
            'role': user.role,
            'face_registered': user.face_registered,
            'face_encodings_count': user.face_encodings_count,
            'status': user.status,
            'last_login': user.last_login,
            'date_joined': user.date_joined,
            'family': {
                'id': user.family.id,
                'name': user.family.family_name,
                'code': user.family.family_code,
                'member_count': user.family.member_count
            } if user.family else None
        })


class UpdateUserAPIView(APIView):
    """更新用户信息"""
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        user = request.user
        
        # 更新可编辑字段
        if 'display_name' in request.data:
            user.display_name = request.data['display_name']
        if 'email' in request.data:
            user.email = request.data['email']
        if 'phone' in request.data:
            user.phone = request.data['phone']
        
        user.save()
        
        return Response({
            'message': '更新成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'display_name': user.display_name,
                'email': user.email,
                'phone': user.phone
            }
        })


class ChangePasswordAPIView(APIView):
    """修改密码"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response({
                'error': '旧密码和新密码不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证旧密码
        if not user.check_password(old_password):
            return Response({
                'error': '旧密码错误'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 设置新密码
        user.set_password(new_password)
        user.save()
        
        return Response({
            'message': '密码修改成功'
        })


class RegisterFaceAPIView(APIView):
    """注册人脸API（支持多张照片）"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        # 检查是否有上传的图片
        images = []
        for i in range(1, 6):  # 支持最多5张照片
            img_key = f'image{i}'
            if img_key in request.FILES:
                images.append(request.FILES[img_key])
            elif img_key in request.data:
                # 支持base64格式
                try:
                    img_data = request.data[img_key]
                    if img_data.startswith('data:image'):
                        img_data = img_data.split(',')[1]
                    img_bytes = base64.b64decode(img_data)
                    images.append(ContentFile(img_bytes, name=f'{user.username}_{i}.jpg'))
                except Exception as e:
                    pass
        
        if not images:
            return Response({
                'error': '请至少上传一张人脸照片'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 保存人脸照片并提取特征
        try:
            import cv2
            import numpy as np
            
            success_count = 0
            for idx, image in enumerate(images):
                # 保存照片
                photo_dir = os.path.join('media', 'faces_db', user.username)
                os.makedirs(photo_dir, exist_ok=True)
                photo_path = os.path.join(photo_dir, f'face_{idx+1}.jpg')
                
                with open(photo_path, 'wb') as f:
                    for chunk in image.chunks():
                        f.write(chunk)
                
                # 读取图片
                img = cv2.imread(photo_path)
                if img is None:
                    continue
                
                # 提取人脸特征
                try:
                    embedding = face_recognition_service.embed(img)
                    
                    # 保存到数据库
                    FaceEncoding.objects.create(
                        user=user,
                        encoding_vector=embedding.tobytes(),
                        encoding_json=embedding.tolist(),
                        photo_path=photo_path,
                        is_primary=(success_count == 0)
                    )
                    success_count += 1
                except Exception as e:
                    print(f"[ERROR] 提取人脸特征失败: {e}")
                    continue
            
            if success_count == 0:
                return Response({
                    'error': '未能从照片中检测到人脸，请确保照片清晰且包含人脸'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 更新用户状态
            user.face_registered = True
            user.face_encodings_count = success_count
            user.save()
            
            return Response({
                'message': f'人脸注册成功，已注册{success_count}张照片',
                'face_count': success_count
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'人脸注册失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyFaceAPIView(APIView):
    """验证人脸API"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # 获取上传的照片
        if 'image' not in request.FILES and 'image' not in request.data:
            return Response({
                'error': '请上传人脸照片'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            import cv2
            import numpy as np
            from io import BytesIO
            
            # 读取图片
            if 'image' in request.FILES:
                image = request.FILES['image']
                img_bytes = image.read()
            else:
                # base64格式
                img_data = request.data['image']
                if img_data.startswith('data:image'):
                    img_data = img_data.split(',')[1]
                img_bytes = base64.b64decode(img_data)
            
            # 转换为OpenCV格式
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return Response({
                    'error': '无效的图片格式'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 人脸识别
            recognized_user, distance = face_recognition_service.recognize(img)
            
            if recognized_user is None:
                return Response({
                    'verified': False,
                    'message': '未识别到注册的人脸',
                    'distance': float(distance)
                })
            
            # 检查是否是当前用户
            is_current_user = (recognized_user.id == request.user.id)
            
            return Response({
                'verified': True,
                'is_current_user': is_current_user,
                'recognized_user': {
                    'id': recognized_user.id,
                    'username': recognized_user.username,
                    'display_name': recognized_user.display_name
                },
                'distance': float(distance),
                'message': '人脸验证成功'
            })
            
        except Exception as e:
            return Response({
                'error': f'人脸验证失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ValidateInviteAPIView(APIView):
    """验证邀请码API"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        invite_code = request.data.get('code')
        
        if not invite_code:
            return Response({
                'error': '邀请码不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            invite = InviteCode.objects.select_related('family').get(code=invite_code)
            
            if not invite.is_valid():
                return Response({
                    'valid': False,
                    'error': '邀请码已失效'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'valid': True,
                'username': invite.username_for,
                'display_name': invite.display_name_for,
                'family': {
                    'id': invite.family.id,
                    'name': invite.family.family_name
                }
            })
            
        except InviteCode.DoesNotExist:
            return Response({
                'valid': False,
                'error': '邀请码不存在'
            }, status=status.HTTP_404_NOT_FOUND)


class AcceptInviteAPIView(APIView):
    """接受邀请API（同注册）"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        # 直接调用注册API
        register_view = RegisterAPIView()
        return register_view.post(request)