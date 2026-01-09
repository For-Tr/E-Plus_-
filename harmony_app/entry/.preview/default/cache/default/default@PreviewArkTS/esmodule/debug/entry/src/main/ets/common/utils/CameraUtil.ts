import camera from "@ohos:multimedia.camera";
import image from "@ohos:multimedia.image";
class CameraUtil {
    private static instance: CameraUtil;
    private cameraManager: camera.CameraManager | null = null;
    private constructor() { }
    public static getInstance(): CameraUtil {
        if (!CameraUtil.instance) {
            CameraUtil.instance = new CameraUtil();
        }
        return CameraUtil.instance;
    }
    /**
     * 初始化相机管理器
     */
    async init(context: Context): Promise<boolean> {
        try {
            this.cameraManager = camera.getCameraManager(context);
            console.info('[CameraUtil] Camera manager initialized');
            return true;
        }
        catch (error) {
            console.error('[CameraUtil] Init failed:', JSON.stringify(error));
            return false;
        }
    }
    /**
     * 拍照并转换为Base64
     */
    async takePictureAsBase64(): Promise<string | null> {
        try {
            if (!this.cameraManager) {
                console.error('[CameraUtil] Camera manager not initialized');
                return null;
            }
            // 获取相机列表
            const cameras = this.cameraManager.getSupportedCameras();
            if (cameras.length === 0) {
                console.error('[CameraUtil] No camera available');
                return null;
            }
            // 使用前置摄像头(用于人脸识别)
            const frontCamera = cameras.find(cam => cam.cameraPosition === camera.CameraPosition.CAMERA_POSITION_FRONT);
            const targetCamera = frontCamera || cameras[0];
            console.info(`[CameraUtil] Using camera: ${targetCamera.cameraId}`);
            // 创建相机输入
            const cameraInput = this.cameraManager.createCameraInput(targetCamera);
            await cameraInput.open();
            // 创建预览输出和拍照输出
            const previewOutput = this.cameraManager.createPreviewOutput();
            const photoOutput = this.cameraManager.createPhotoOutput();
            // 创建捕获会话
            const captureSession = this.cameraManager.createCaptureSession();
            await captureSession.beginConfig();
            captureSession.addInput(cameraInput);
            captureSession.addOutput(previewOutput);
            captureSession.addOutput(photoOutput);
            await captureSession.commitConfig();
            await captureSession.start();
            // 拍照
            return new Promise((resolve, reject) => {
                photoOutput.on('photoAvailable', async (photo) => {
                    try {
                        // 获取图片缓冲区
                        const imageBuffer = await photo.main.getComponent(image.ComponentType.JPEG);
                        if (!imageBuffer || !imageBuffer.byteBuffer) {
                            reject(new Error('Failed to get image buffer'));
                            return;
                        }
                        // 转换为Base64
                        const base64String = this.arrayBufferToBase64(imageBuffer.byteBuffer);
                        // 清理资源
                        await captureSession.stop();
                        await captureSession.release();
                        await cameraInput.close();
                        resolve(base64String);
                    }
                    catch (error) {
                        console.error('[CameraUtil] Photo process error:', JSON.stringify(error));
                        reject(error);
                    }
                });
                // 触发拍照
                photoOutput.capture().catch(error => {
                    console.error('[CameraUtil] Capture error:', JSON.stringify(error));
                    reject(error);
                });
                // 超时处理
                setTimeout(() => {
                    reject(new Error('Capture timeout'));
                }, 10000);
            });
        }
        catch (error) {
            console.error('[CameraUtil] Take picture failed:', JSON.stringify(error));
            return null;
        }
    }
    /**
     * ArrayBuffer转Base64
     */
    private arrayBufferToBase64(buffer: ArrayBuffer): string {
        let binary = '';
        const bytes = new Uint8Array(buffer);
        const len = bytes.byteLength;
        for (let i = 0; i < len; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary);
    }
    /**
     * 压缩图片
     */
    async compressImage(base64String: string, quality: number = 80): Promise<string> {
        try {
            // 简化版本:实际应用中可以使用image模块进行压缩
            // 这里直接返回原图
            return base64String;
        }
        catch (error) {
            console.error('[CameraUtil] Compress error:', JSON.stringify(error));
            return base64String;
        }
    }
}
export default CameraUtil.getInstance();
