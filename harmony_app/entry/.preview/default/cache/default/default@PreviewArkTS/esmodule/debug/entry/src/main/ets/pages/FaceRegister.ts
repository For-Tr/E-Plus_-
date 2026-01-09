if (!("finalizeConstruction" in ViewPU.prototype)) {
    Reflect.set(ViewPU.prototype, "finalizeConstruction", () => { });
}
interface FaceRegister_Params {
    isLoading?: boolean;
    message?: string;
    capturedImage?: string;
    step?: number;
}
import router from "@ohos:router";
import promptAction from "@ohos:promptAction";
import HttpUtil from "@bundle:com.family.emotion/entry/ets/common/utils/HttpUtil";
import StorageUtil from "@bundle:com.family.emotion/entry/ets/common/utils/StorageUtil";
import CameraUtil from "@bundle:com.family.emotion/entry/ets/common/utils/CameraUtil";
import { ApiEndpoints, StorageKeys, AppConfig, ErrorMessages } from "@bundle:com.family.emotion/entry/ets/common/constants/AppConstants";
class FaceRegister extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.__isLoading = new ObservedPropertySimplePU(false, this, "isLoading");
        this.__message = new ObservedPropertySimplePU('', this, "message");
        this.__capturedImage = new ObservedPropertySimplePU('', this, "capturedImage");
        this.__step = new ObservedPropertySimplePU(1 // 1:说明 2:拍照 3:上传
        , this, "step");
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: FaceRegister_Params) {
        if (params.isLoading !== undefined) {
            this.isLoading = params.isLoading;
        }
        if (params.message !== undefined) {
            this.message = params.message;
        }
        if (params.capturedImage !== undefined) {
            this.capturedImage = params.capturedImage;
        }
        if (params.step !== undefined) {
            this.step = params.step;
        }
    }
    updateStateVars(params: FaceRegister_Params) {
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
        this.__isLoading.purgeDependencyOnElmtId(rmElmtId);
        this.__message.purgeDependencyOnElmtId(rmElmtId);
        this.__capturedImage.purgeDependencyOnElmtId(rmElmtId);
        this.__step.purgeDependencyOnElmtId(rmElmtId);
    }
    aboutToBeDeleted() {
        this.__isLoading.aboutToBeDeleted();
        this.__message.aboutToBeDeleted();
        this.__capturedImage.aboutToBeDeleted();
        this.__step.aboutToBeDeleted();
        SubscriberManager.Get().delete(this.id__());
        this.aboutToBeDeletedInternal();
    }
    private __isLoading: ObservedPropertySimplePU<boolean>;
    get isLoading() {
        return this.__isLoading.get();
    }
    set isLoading(newValue: boolean) {
        this.__isLoading.set(newValue);
    }
    private __message: ObservedPropertySimplePU<string>;
    get message() {
        return this.__message.get();
    }
    set message(newValue: string) {
        this.__message.set(newValue);
    }
    private __capturedImage: ObservedPropertySimplePU<string>;
    get capturedImage() {
        return this.__capturedImage.get();
    }
    set capturedImage(newValue: string) {
        this.__capturedImage.set(newValue);
    }
    private __step: ObservedPropertySimplePU<number>; // 1:说明 2:拍照 3:上传
    get step() {
        return this.__step.get();
    }
    set step(newValue: number) {
        this.__step.set(newValue);
    }
    async aboutToAppear() {
        // 初始化相机
        await CameraUtil.init(getContext(this));
    }
    /**
     * 拍照
     */
    async handleTakePicture() {
        this.isLoading = true;
        this.message = '正在启动相机...';
        try {
            const photoBase64 = await CameraUtil.takePictureAsBase64();
            if (photoBase64) {
                this.capturedImage = photoBase64;
                this.step = 3;
                this.message = '';
                promptAction.showToast({
                    message: '照片拍摄成功',
                    duration: 1500
                });
            }
            else {
                this.message = ErrorMessages.CAMERA_ERROR;
                promptAction.showToast({
                    message: ErrorMessages.CAMERA_ERROR,
                    duration: 2000
                });
            }
        }
        catch (error) {
            console.error('[FaceRegister] Take picture error:', JSON.stringify(error));
            this.message = ErrorMessages.CAMERA_ERROR;
            promptAction.showToast({
                message: ErrorMessages.CAMERA_ERROR,
                duration: 2000
            });
        }
        finally {
            this.isLoading = false;
        }
    }
    /**
     * 上传人脸照片
     */
    async handleUpload() {
        if (!this.capturedImage) {
            promptAction.showToast({
                message: '请先拍照',
                duration: 2000
            });
            return;
        }
        this.isLoading = true;
        this.message = '正在注册人脸...';
        try {
            const response = await HttpUtil.uploadImage(ApiEndpoints.FACE_REGISTER, this.capturedImage, 'photo');
            if (response.success) {
                // 更新本地人脸注册状态
                await StorageUtil.setBoolean(StorageKeys.IS_FACE_REGISTERED, true);
                promptAction.showToast({
                    message: '人脸注册成功!',
                    duration: 2000
                });
                // 跳转到主页
                setTimeout(() => {
                    router.replaceUrl({
                        url: AppConfig.PAGE_HOME
                    });
                }, 1500);
            }
            else {
                this.message = response.error || ErrorMessages.FACE_REGISTER_FAILED;
                promptAction.showToast({
                    message: response.error || ErrorMessages.FACE_REGISTER_FAILED,
                    duration: 3000
                });
            }
        }
        catch (error) {
            console.error('[FaceRegister] Upload error:', JSON.stringify(error));
            this.message = ErrorMessages.NETWORK_ERROR;
            promptAction.showToast({
                message: ErrorMessages.NETWORK_ERROR,
                duration: 3000
            });
        }
        finally {
            this.isLoading = false;
        }
    }
    /**
     * 重新拍照
     */
    handleRetake() {
        this.capturedImage = '';
        this.step = 2;
        this.message = '';
    }
    /**
     * 跳过注册
     */
    handleSkip() {
        router.replaceUrl({
            url: AppConfig.PAGE_HOME
        });
    }
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create();
            Column.debugLine("entry/src/main/ets/pages/FaceRegister.ets(137:5)", "entry");
            Column.width('100%');
            Column.height('100%');
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 顶部标题
            Row.create();
            Row.debugLine("entry/src/main/ets/pages/FaceRegister.ets(139:7)", "entry");
            // 顶部标题
            Row.width('100%');
            // 顶部标题
            Row.height(56);
            // 顶部标题
            Row.padding({ left: 20, right: 20 });
            // 顶部标题
            Row.backgroundColor('#FFFFFF');
            // 顶部标题
            Row.justifyContent(FlexAlign.Center);
        }, Row);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('人脸注册');
            Text.debugLine("entry/src/main/ets/pages/FaceRegister.ets(140:9)", "entry");
            Text.fontSize(20);
            Text.fontWeight(FontWeight.Medium);
            Text.fontColor('#333');
        }, Text);
        Text.pop();
        // 顶部标题
        Row.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 主内容区域
            Column.create();
            Column.debugLine("entry/src/main/ets/pages/FaceRegister.ets(152:7)", "entry");
            // 主内容区域
            Column.layoutWeight(1);
            // 主内容区域
            Column.backgroundColor('#F5F5F5');
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            If.create();
            if (this.step === 1) {
                this.ifElseBranchUpdateFunction(0, () => {
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        // 说明页面
                        Column.create();
                        Column.debugLine("entry/src/main/ets/pages/FaceRegister.ets(155:11)", "entry");
                        // 说明页面
                        Column.width('100%');
                        // 说明页面
                        Column.padding(30);
                    }, Column);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Image.create({ "id": 16777231, "type": 20000, params: [], "bundleName": "com.family.emotion", "moduleName": "entry" });
                        Image.debugLine("entry/src/main/ets/pages/FaceRegister.ets(156:13)", "entry");
                        Image.width(200);
                        Image.height(200);
                        Image.margin({ bottom: 30 });
                    }, Image);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create('首次使用需要注册人脸');
                        Text.debugLine("entry/src/main/ets/pages/FaceRegister.ets(161:13)", "entry");
                        Text.fontSize(20);
                        Text.fontWeight(FontWeight.Medium);
                        Text.fontColor('#333');
                        Text.margin({ bottom: 15 });
                    }, Text);
                    Text.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Column.create();
                        Column.debugLine("entry/src/main/ets/pages/FaceRegister.ets(167:13)", "entry");
                        Column.alignItems(HorizontalAlign.Start);
                        Column.margin({ bottom: 40 });
                    }, Column);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create('• 请确保光线充足');
                        Text.debugLine("entry/src/main/ets/pages/FaceRegister.ets(168:15)", "entry");
                        Text.fontSize(16);
                        Text.fontColor('#666');
                        Text.margin({ bottom: 8 });
                    }, Text);
                    Text.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create('• 正对摄像头,保持面部清晰');
                        Text.debugLine("entry/src/main/ets/pages/FaceRegister.ets(173:15)", "entry");
                        Text.fontSize(16);
                        Text.fontColor('#666');
                        Text.margin({ bottom: 8 });
                    }, Text);
                    Text.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create('• 摘下眼镜和口罩');
                        Text.debugLine("entry/src/main/ets/pages/FaceRegister.ets(178:15)", "entry");
                        Text.fontSize(16);
                        Text.fontColor('#666');
                        Text.margin({ bottom: 8 });
                    }, Text);
                    Text.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create('• 保持自然表情');
                        Text.debugLine("entry/src/main/ets/pages/FaceRegister.ets(183:15)", "entry");
                        Text.fontSize(16);
                        Text.fontColor('#666');
                    }, Text);
                    Text.pop();
                    Column.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Button.createWithLabel('开始拍照');
                        Button.debugLine("entry/src/main/ets/pages/FaceRegister.ets(190:13)", "entry");
                        Button.width('80%');
                        Button.height(50);
                        Button.fontSize(18);
                        Button.fontColor('#FFFFFF');
                        Button.backgroundColor('#007DFF');
                        Button.borderRadius(10);
                        Button.onClick(() => {
                            this.step = 2;
                            this.handleTakePicture();
                        });
                    }, Button);
                    Button.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Button.createWithLabel('稍后注册');
                        Button.debugLine("entry/src/main/ets/pages/FaceRegister.ets(202:13)", "entry");
                        Button.width('80%');
                        Button.height(50);
                        Button.fontSize(16);
                        Button.fontColor('#666');
                        Button.backgroundColor('#FFFFFF');
                        Button.border({ width: 1, color: '#DDDDDD' });
                        Button.borderRadius(10);
                        Button.margin({ top: 15 });
                        Button.onClick(() => {
                            this.handleSkip();
                        });
                    }, Button);
                    Button.pop();
                    // 说明页面
                    Column.pop();
                });
            }
            else if (this.step === 2) {
                this.ifElseBranchUpdateFunction(1, () => {
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        // 拍照中
                        Column.create();
                        Column.debugLine("entry/src/main/ets/pages/FaceRegister.ets(220:11)", "entry");
                        // 拍照中
                        Column.width('100%');
                    }, Column);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create('请正对摄像头');
                        Text.debugLine("entry/src/main/ets/pages/FaceRegister.ets(221:13)", "entry");
                        Text.fontSize(18);
                        Text.fontColor('#333');
                        Text.margin({ top: 50, bottom: 30 });
                    }, Text);
                    Text.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        // 相机预览区域占位
                        Column.create();
                        Column.debugLine("entry/src/main/ets/pages/FaceRegister.ets(227:13)", "entry");
                        // 相机预览区域占位
                        Column.width(300);
                        // 相机预览区域占位
                        Column.height(400);
                        // 相机预览区域占位
                        Column.backgroundColor('#000000');
                        // 相机预览区域占位
                        Column.borderRadius(15);
                        // 相机预览区域占位
                        Column.justifyContent(FlexAlign.Center);
                    }, Column);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create('📷');
                        Text.debugLine("entry/src/main/ets/pages/FaceRegister.ets(228:15)", "entry");
                        Text.fontSize(80);
                    }, Text);
                    Text.pop();
                    // 相机预览区域占位
                    Column.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        If.create();
                        if (this.isLoading) {
                            this.ifElseBranchUpdateFunction(0, () => {
                                this.observeComponentCreation2((elmtId, isInitialRender) => {
                                    Text.create(this.message || '准备中...');
                                    Text.debugLine("entry/src/main/ets/pages/FaceRegister.ets(238:15)", "entry");
                                    Text.fontSize(16);
                                    Text.fontColor('#666');
                                    Text.margin({ top: 20 });
                                }, Text);
                                Text.pop();
                            });
                        }
                        else {
                            this.ifElseBranchUpdateFunction(1, () => {
                            });
                        }
                    }, If);
                    If.pop();
                    // 拍照中
                    Column.pop();
                });
            }
            else if (this.step === 3) {
                this.ifElseBranchUpdateFunction(2, () => {
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        // 照片预览和上传
                        Column.create();
                        Column.debugLine("entry/src/main/ets/pages/FaceRegister.ets(248:11)", "entry");
                        // 照片预览和上传
                        Column.width('100%');
                    }, Column);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create('照片预览');
                        Text.debugLine("entry/src/main/ets/pages/FaceRegister.ets(249:13)", "entry");
                        Text.fontSize(18);
                        Text.fontWeight(FontWeight.Medium);
                        Text.fontColor('#333');
                        Text.margin({ top: 20, bottom: 20 });
                    }, Text);
                    Text.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        // 显示拍摄的照片
                        Image.create(`data:image/jpeg;base64,${this.capturedImage}`);
                        Image.debugLine("entry/src/main/ets/pages/FaceRegister.ets(256:13)", "entry");
                        // 显示拍摄的照片
                        Image.width(300);
                        // 显示拍摄的照片
                        Image.height(400);
                        // 显示拍摄的照片
                        Image.objectFit(ImageFit.Cover);
                        // 显示拍摄的照片
                        Image.borderRadius(15);
                        // 显示拍摄的照片
                        Image.margin({ bottom: 30 });
                    }, Image);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Row.create();
                        Row.debugLine("entry/src/main/ets/pages/FaceRegister.ets(263:13)", "entry");
                        Row.width('85%');
                        Row.justifyContent(FlexAlign.SpaceBetween);
                    }, Row);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Button.createWithLabel('重新拍照');
                        Button.debugLine("entry/src/main/ets/pages/FaceRegister.ets(264:15)", "entry");
                        Button.width('45%');
                        Button.height(50);
                        Button.fontSize(16);
                        Button.fontColor('#666');
                        Button.backgroundColor('#FFFFFF');
                        Button.border({ width: 1, color: '#DDDDDD' });
                        Button.borderRadius(10);
                        Button.enabled(!this.isLoading);
                        Button.onClick(() => {
                            this.handleRetake();
                        });
                    }, Button);
                    Button.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Button.createWithLabel(this.isLoading ? '上传中...' : '确认上传');
                        Button.debugLine("entry/src/main/ets/pages/FaceRegister.ets(277:15)", "entry");
                        Button.width('45%');
                        Button.height(50);
                        Button.fontSize(16);
                        Button.fontColor('#FFFFFF');
                        Button.backgroundColor(this.isLoading ? '#CCCCCC' : '#007DFF');
                        Button.borderRadius(10);
                        Button.enabled(!this.isLoading);
                        Button.onClick(() => {
                            this.handleUpload();
                        });
                    }, Button);
                    Button.pop();
                    Row.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        If.create();
                        if (this.message) {
                            this.ifElseBranchUpdateFunction(0, () => {
                                this.observeComponentCreation2((elmtId, isInitialRender) => {
                                    Text.create(this.message);
                                    Text.debugLine("entry/src/main/ets/pages/FaceRegister.ets(293:15)", "entry");
                                    Text.fontSize(14);
                                    Text.fontColor('#FF0000');
                                    Text.margin({ top: 15 });
                                }, Text);
                                Text.pop();
                            });
                        }
                        else {
                            this.ifElseBranchUpdateFunction(1, () => {
                            });
                        }
                    }, If);
                    If.pop();
                    // 照片预览和上传
                    Column.pop();
                });
            }
            else {
                this.ifElseBranchUpdateFunction(3, () => {
                });
            }
        }, If);
        If.pop();
        // 主内容区域
        Column.pop();
        Column.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
    static getEntryName(): string {
        return "FaceRegister";
    }
}
registerNamedRoute(() => new FaceRegister(undefined, {}), "", { bundleName: "com.family.emotion", moduleName: "entry", pagePath: "pages/FaceRegister", pageFullPath: "entry/src/main/ets/pages/FaceRegister", integratedHsp: "false", moduleType: "followWithHap" });
