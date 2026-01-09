if (!("finalizeConstruction" in ViewPU.prototype)) {
    Reflect.set(ViewPU.prototype, "finalizeConstruction", () => { });
}
interface Checkin_Params {
    isLoading?: boolean;
    message?: string;
    currentTask?: any;
    capturedImage?: string;
    checkinResult?: CheckinRecord | null;
    step?: number;
}
import router from "@ohos:router";
import promptAction from "@ohos:promptAction";
import HttpUtil from "@bundle:com.family.emotion/entry/ets/common/utils/HttpUtil";
import CameraUtil from "@bundle:com.family.emotion/entry/ets/common/utils/CameraUtil";
import { ApiEndpoints, EMOTION_NAMES, ErrorMessages } from "@bundle:com.family.emotion/entry/ets/common/constants/AppConstants";
import type { CheckinTaskListResponse } from '../models/CheckinTask';
import type { CheckinCreateRequest, CheckinRecord } from '../models/CheckinRecord';
class Checkin extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.__isLoading = new ObservedPropertySimplePU(false, this, "isLoading");
        this.__message = new ObservedPropertySimplePU('', this, "message");
        this.__currentTask = new ObservedPropertyObjectPU(null, this, "currentTask");
        this.__capturedImage = new ObservedPropertySimplePU('', this, "capturedImage");
        this.__checkinResult = new ObservedPropertyObjectPU(null, this, "checkinResult");
        this.__step = new ObservedPropertySimplePU(1 // 1:任务说明 2:拍照 3:结果展示
        , this, "step");
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: Checkin_Params) {
        if (params.isLoading !== undefined) {
            this.isLoading = params.isLoading;
        }
        if (params.message !== undefined) {
            this.message = params.message;
        }
        if (params.currentTask !== undefined) {
            this.currentTask = params.currentTask;
        }
        if (params.capturedImage !== undefined) {
            this.capturedImage = params.capturedImage;
        }
        if (params.checkinResult !== undefined) {
            this.checkinResult = params.checkinResult;
        }
        if (params.step !== undefined) {
            this.step = params.step;
        }
    }
    updateStateVars(params: Checkin_Params) {
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
        this.__isLoading.purgeDependencyOnElmtId(rmElmtId);
        this.__message.purgeDependencyOnElmtId(rmElmtId);
        this.__currentTask.purgeDependencyOnElmtId(rmElmtId);
        this.__capturedImage.purgeDependencyOnElmtId(rmElmtId);
        this.__checkinResult.purgeDependencyOnElmtId(rmElmtId);
        this.__step.purgeDependencyOnElmtId(rmElmtId);
    }
    aboutToBeDeleted() {
        this.__isLoading.aboutToBeDeleted();
        this.__message.aboutToBeDeleted();
        this.__currentTask.aboutToBeDeleted();
        this.__capturedImage.aboutToBeDeleted();
        this.__checkinResult.aboutToBeDeleted();
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
    private __currentTask: ObservedPropertyObjectPU<any>;
    get currentTask() {
        return this.__currentTask.get();
    }
    set currentTask(newValue: any) {
        this.__currentTask.set(newValue);
    }
    private __capturedImage: ObservedPropertySimplePU<string>;
    get capturedImage() {
        return this.__capturedImage.get();
    }
    set capturedImage(newValue: string) {
        this.__capturedImage.set(newValue);
    }
    private __checkinResult: ObservedPropertyObjectPU<CheckinRecord | null>;
    get checkinResult() {
        return this.__checkinResult.get();
    }
    set checkinResult(newValue: CheckinRecord | null) {
        this.__checkinResult.set(newValue);
    }
    private __step: ObservedPropertySimplePU<number>; // 1:任务说明 2:拍照 3:结果展示
    get step() {
        return this.__step.get();
    }
    set step(newValue: number) {
        this.__step.set(newValue);
    }
    async aboutToAppear() {
        await CameraUtil.init(getContext(this));
        await this.loadTask();
    }
    /**
     * 加载打卡任务
     */
    async loadTask() {
        this.isLoading = true;
        try {
            const response = await HttpUtil.get<CheckinTaskListResponse>(ApiEndpoints.CHECKIN_TASKS);
            if (response.success && response.data && response.data.results.length > 0) {
                // 获取第一个活跃任务
                this.currentTask = response.data.results[0];
                console.info('[Checkin] Task loaded:', JSON.stringify(this.currentTask));
            }
            else {
                promptAction.showToast({
                    message: '暂无打卡任务',
                    duration: 2000
                });
                setTimeout(() => {
                    router.back();
                }, 1500);
            }
        }
        catch (error) {
            console.error('[Checkin] Load task error:', JSON.stringify(error));
            promptAction.showToast({
                message: ErrorMessages.NETWORK_ERROR,
                duration: 2000
            });
        }
        finally {
            this.isLoading = false;
        }
    }
    /**
     * 开始拍照
     */
    async handleStartCapture() {
        this.step = 2;
        this.isLoading = true;
        this.message = '正在启动相机...';
        try {
            const photoBase64 = await CameraUtil.takePictureAsBase64();
            if (photoBase64) {
                this.capturedImage = photoBase64;
                this.message = '';
                // 直接提交打卡
                await this.submitCheckin();
            }
            else {
                this.message = ErrorMessages.CAMERA_ERROR;
                promptAction.showToast({
                    message: ErrorMessages.CAMERA_ERROR,
                    duration: 2000
                });
                this.step = 1;
            }
        }
        catch (error) {
            console.error('[Checkin] Capture error:', JSON.stringify(error));
            this.message = ErrorMessages.CAMERA_ERROR;
            this.step = 1;
        }
        finally {
            this.isLoading = false;
        }
    }
    /**
     * 提交打卡
     */
    async submitCheckin() {
        this.isLoading = true;
        this.message = '正在识别人脸和情绪...';
        try {
            const requestData: CheckinCreateRequest = {
                task_id: this.currentTask.id,
                photo: this.capturedImage
            };
            const response = await HttpUtil.post<CheckinRecord>(ApiEndpoints.CHECKIN_CREATE, requestData);
            if (response.success && response.data) {
                this.checkinResult = response.data;
                this.step = 3;
                this.message = '';
                promptAction.showToast({
                    message: '打卡成功!',
                    duration: 2000
                });
            }
            else {
                this.message = response.error || ErrorMessages.CHECKIN_FAILED;
                this.step = 1;
                promptAction.showToast({
                    message: response.error || ErrorMessages.CHECKIN_FAILED,
                    duration: 3000
                });
            }
        }
        catch (error) {
            console.error('[Checkin] Submit error:', JSON.stringify(error));
            this.message = ErrorMessages.NETWORK_ERROR;
            this.step = 1;
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
     * 完成打卡,返回主页
     */
    handleFinish() {
        router.back();
    }
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create();
            Column.debugLine("entry/src/main/ets/pages/Checkin.ets(150:5)", "entry");
            Column.width('100%');
            Column.height('100%');
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 顶部标题栏
            Row.create();
            Row.debugLine("entry/src/main/ets/pages/Checkin.ets(152:7)", "entry");
            // 顶部标题栏
            Row.width('100%');
            // 顶部标题栏
            Row.height(56);
            // 顶部标题栏
            Row.padding({ left: 20, right: 20 });
            // 顶部标题栏
            Row.backgroundColor('#FFFFFF');
        }, Row);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Image.create($r('app.media.back'));
            Image.debugLine("entry/src/main/ets/pages/Checkin.ets(153:9)", "entry");
            Image.width(24);
            Image.height(24);
            Image.onClick(() => {
                router.back();
            });
        }, Image);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('打卡');
            Text.debugLine("entry/src/main/ets/pages/Checkin.ets(160:9)", "entry");
            Text.fontSize(20);
            Text.fontWeight(FontWeight.Medium);
            Text.fontColor('#333');
            Text.layoutWeight(1);
            Text.textAlign(TextAlign.Center);
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 占位,保持标题居中
            Column.create();
            Column.debugLine("entry/src/main/ets/pages/Checkin.ets(168:9)", "entry");
            // 占位,保持标题居中
            Column.width(24);
            // 占位,保持标题居中
            Column.height(24);
        }, Column);
        // 占位,保持标题居中
        Column.pop();
        // 顶部标题栏
        Row.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 主内容
            Column.create();
            Column.debugLine("entry/src/main/ets/pages/Checkin.ets(178:7)", "entry");
            // 主内容
            Column.layoutWeight(1);
            // 主内容
            Column.backgroundColor('#F5F5F5');
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            If.create();
            if (this.step === 1 && this.currentTask) {
                this.ifElseBranchUpdateFunction(0, () => {
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        // 任务说明页面
                        Column.create();
                        Column.debugLine("entry/src/main/ets/pages/Checkin.ets(181:11)", "entry");
                        // 任务说明页面
                        Column.width('100%');
                    }, Column);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Image.create($r('app.media.checkin_icon'));
                        Image.debugLine("entry/src/main/ets/pages/Checkin.ets(182:13)", "entry");
                        Image.width(100);
                        Image.height(100);
                        Image.margin({ top: 50, bottom: 30 });
                    }, Image);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create(this.currentTask.task_name);
                        Text.debugLine("entry/src/main/ets/pages/Checkin.ets(187:13)", "entry");
                        Text.fontSize(24);
                        Text.fontWeight(FontWeight.Bold);
                        Text.fontColor('#333');
                        Text.margin({ bottom: 15 });
                    }, Text);
                    Text.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Column.create();
                        Column.debugLine("entry/src/main/ets/pages/Checkin.ets(193:13)", "entry");
                        Column.width('85%');
                        Column.margin({ bottom: 50 });
                    }, Column);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create('准备开始打卡');
                        Text.debugLine("entry/src/main/ets/pages/Checkin.ets(194:15)", "entry");
                        Text.fontSize(18);
                        Text.fontColor('#666');
                        Text.margin({ bottom: 20 });
                    }, Text);
                    Text.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Column.create();
                        Column.debugLine("entry/src/main/ets/pages/Checkin.ets(199:15)", "entry");
                        Column.alignItems(HorizontalAlign.Start);
                        Column.padding(20);
                        Column.backgroundColor('#FFF9E6');
                        Column.borderRadius(10);
                    }, Column);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create('• 请正对摄像头');
                        Text.debugLine("entry/src/main/ets/pages/Checkin.ets(200:17)", "entry");
                        Text.fontSize(16);
                        Text.fontColor('#666');
                        Text.margin({ bottom: 8 });
                    }, Text);
                    Text.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create('• 保持面部清晰可见');
                        Text.debugLine("entry/src/main/ets/pages/Checkin.ets(205:17)", "entry");
                        Text.fontSize(16);
                        Text.fontColor('#666');
                        Text.margin({ bottom: 8 });
                    }, Text);
                    Text.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create('• 系统将自动识别您的情绪');
                        Text.debugLine("entry/src/main/ets/pages/Checkin.ets(210:17)", "entry");
                        Text.fontSize(16);
                        Text.fontColor('#666');
                        Text.margin({ bottom: 8 });
                    }, Text);
                    Text.pop();
                    Column.pop();
                    Column.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Button.createWithLabel('开始打卡');
                        Button.debugLine("entry/src/main/ets/pages/Checkin.ets(223:13)", "entry");
                        Button.width('70%');
                        Button.height(55);
                        Button.fontSize(20);
                        Button.fontColor('#FFFFFF');
                        Button.backgroundColor('#007DFF');
                        Button.borderRadius(15);
                        Button.enabled(!this.isLoading);
                        Button.onClick(() => {
                            this.handleStartCapture();
                        });
                    }, Button);
                    Button.pop();
                    // 任务说明页面
                    Column.pop();
                });
            }
            else if (this.step === 2) {
                this.ifElseBranchUpdateFunction(1, () => {
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        // 拍照中
                        Column.create();
                        Column.debugLine("entry/src/main/ets/pages/Checkin.ets(239:11)", "entry");
                    }, Column);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create('请保持面部在框内');
                        Text.debugLine("entry/src/main/ets/pages/Checkin.ets(240:13)", "entry");
                        Text.fontSize(18);
                        Text.fontColor('#333');
                        Text.margin({ top: 50, bottom: 30 });
                    }, Text);
                    Text.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        // 相机预览占位
                        Column.create();
                        Column.debugLine("entry/src/main/ets/pages/Checkin.ets(246:13)", "entry");
                        // 相机预览占位
                        Column.width(300);
                        // 相机预览占位
                        Column.height(400);
                        // 相机预览占位
                        Column.backgroundColor('#000000');
                        // 相机预览占位
                        Column.borderRadius(15);
                        // 相机预览占位
                        Column.justifyContent(FlexAlign.Center);
                    }, Column);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create('📷');
                        Text.debugLine("entry/src/main/ets/pages/Checkin.ets(247:15)", "entry");
                        Text.fontSize(80);
                    }, Text);
                    Text.pop();
                    // 相机预览占位
                    Column.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create(this.message);
                        Text.debugLine("entry/src/main/ets/pages/Checkin.ets(256:13)", "entry");
                        Text.fontSize(16);
                        Text.fontColor('#666');
                        Text.margin({ top: 20 });
                    }, Text);
                    Text.pop();
                    // 拍照中
                    Column.pop();
                });
            }
            else if (this.step === 3 && this.checkinResult) {
                this.ifElseBranchUpdateFunction(2, () => {
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        // 结果展示
                        Column.create();
                        Column.debugLine("entry/src/main/ets/pages/Checkin.ets(264:11)", "entry");
                        // 结果展示
                        Column.width('100%');
                    }, Column);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        // 成功图标
                        Text.create('✓');
                        Text.debugLine("entry/src/main/ets/pages/Checkin.ets(266:13)", "entry");
                        // 成功图标
                        Text.fontSize(80);
                        // 成功图标
                        Text.fontColor('#52C41A');
                        // 成功图标
                        Text.margin({ top: 50, bottom: 20 });
                    }, Text);
                    // 成功图标
                    Text.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create('打卡成功!');
                        Text.debugLine("entry/src/main/ets/pages/Checkin.ets(271:13)", "entry");
                        Text.fontSize(28);
                        Text.fontWeight(FontWeight.Bold);
                        Text.fontColor('#333');
                        Text.margin({ bottom: 40 });
                    }, Text);
                    Text.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        // 结果卡片
                        Column.create();
                        Column.debugLine("entry/src/main/ets/pages/Checkin.ets(278:13)", "entry");
                        // 结果卡片
                        Column.width('85%');
                        // 结果卡片
                        Column.padding(25);
                        // 结果卡片
                        Column.backgroundColor('#FFFFFF');
                        // 结果卡片
                        Column.borderRadius(15);
                        // 结果卡片
                        Column.shadow({
                            radius: 15,
                            color: '#00000010',
                            offsetX: 0,
                            offsetY: 3
                        });
                        // 结果卡片
                        Column.margin({ bottom: 50 });
                    }, Column);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        // 打卡时间
                        Row.create();
                        Row.debugLine("entry/src/main/ets/pages/Checkin.ets(280:15)", "entry");
                        // 打卡时间
                        Row.width('100%');
                        // 打卡时间
                        Row.margin({ bottom: 15 });
                    }, Row);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create('打卡时间:');
                        Text.debugLine("entry/src/main/ets/pages/Checkin.ets(281:17)", "entry");
                        Text.fontSize(16);
                        Text.fontColor('#666');
                    }, Text);
                    Text.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Blank.create();
                        Blank.debugLine("entry/src/main/ets/pages/Checkin.ets(284:17)", "entry");
                    }, Blank);
                    Blank.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create(new Date(this.checkinResult.checkin_time).toLocaleString('zh-CN'));
                        Text.debugLine("entry/src/main/ets/pages/Checkin.ets(285:17)", "entry");
                        Text.fontSize(16);
                        Text.fontColor('#333');
                    }, Text);
                    Text.pop();
                    // 打卡时间
                    Row.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        // 打卡状态
                        Row.create();
                        Row.debugLine("entry/src/main/ets/pages/Checkin.ets(293:15)", "entry");
                        // 打卡状态
                        Row.width('100%');
                        // 打卡状态
                        Row.margin({ bottom: 15 });
                    }, Row);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create('打卡状态:');
                        Text.debugLine("entry/src/main/ets/pages/Checkin.ets(294:17)", "entry");
                        Text.fontSize(16);
                        Text.fontColor('#666');
                    }, Text);
                    Text.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Blank.create();
                        Blank.debugLine("entry/src/main/ets/pages/Checkin.ets(297:17)", "entry");
                    }, Blank);
                    Blank.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create(this.checkinResult.status === 'on_time' ? '准时' :
                            this.checkinResult.status === 'late' ? '迟到' : '补签');
                        Text.debugLine("entry/src/main/ets/pages/Checkin.ets(298:17)", "entry");
                        Text.fontSize(16);
                        Text.fontColor(this.checkinResult.status === 'on_time' ? '#52C41A' :
                            this.checkinResult.status === 'late' ? '#FAAD14' : '#F5222D');
                        Text.fontWeight(FontWeight.Medium);
                    }, Text);
                    Text.pop();
                    // 打卡状态
                    Row.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        If.create();
                        // 识别情绪
                        if (this.checkinResult.emotion) {
                            this.ifElseBranchUpdateFunction(0, () => {
                                this.observeComponentCreation2((elmtId, isInitialRender) => {
                                    Row.create();
                                    Row.debugLine("entry/src/main/ets/pages/Checkin.ets(314:17)", "entry");
                                    Row.width('100%');
                                    Row.margin({ bottom: 15 });
                                }, Row);
                                this.observeComponentCreation2((elmtId, isInitialRender) => {
                                    Text.create('当前情绪:');
                                    Text.debugLine("entry/src/main/ets/pages/Checkin.ets(315:19)", "entry");
                                    Text.fontSize(16);
                                    Text.fontColor('#666');
                                }, Text);
                                Text.pop();
                                this.observeComponentCreation2((elmtId, isInitialRender) => {
                                    Blank.create();
                                    Blank.debugLine("entry/src/main/ets/pages/Checkin.ets(318:19)", "entry");
                                }, Blank);
                                Blank.pop();
                                this.observeComponentCreation2((elmtId, isInitialRender) => {
                                    Text.create(EMOTION_NAMES[this.checkinResult.emotion] || this.checkinResult.emotion);
                                    Text.debugLine("entry/src/main/ets/pages/Checkin.ets(319:19)", "entry");
                                    Text.fontSize(20);
                                    Text.fontWeight(FontWeight.Medium);
                                }, Text);
                                Text.pop();
                                Row.pop();
                            });
                        }
                        // 置信度
                        else {
                            this.ifElseBranchUpdateFunction(1, () => {
                            });
                        }
                    }, If);
                    If.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        If.create();
                        // 置信度
                        if (this.checkinResult.emotion_confidence) {
                            this.ifElseBranchUpdateFunction(0, () => {
                                this.observeComponentCreation2((elmtId, isInitialRender) => {
                                    Row.create();
                                    Row.debugLine("entry/src/main/ets/pages/Checkin.ets(329:17)", "entry");
                                    Row.width('100%');
                                }, Row);
                                this.observeComponentCreation2((elmtId, isInitialRender) => {
                                    Text.create('置信度:');
                                    Text.debugLine("entry/src/main/ets/pages/Checkin.ets(330:19)", "entry");
                                    Text.fontSize(16);
                                    Text.fontColor('#666');
                                }, Text);
                                Text.pop();
                                this.observeComponentCreation2((elmtId, isInitialRender) => {
                                    Blank.create();
                                    Blank.debugLine("entry/src/main/ets/pages/Checkin.ets(333:19)", "entry");
                                }, Blank);
                                Blank.pop();
                                this.observeComponentCreation2((elmtId, isInitialRender) => {
                                    Text.create(`${this.checkinResult.emotion_confidence.toFixed(1)}%`);
                                    Text.debugLine("entry/src/main/ets/pages/Checkin.ets(334:19)", "entry");
                                    Text.fontSize(16);
                                    Text.fontColor('#333');
                                }, Text);
                                Text.pop();
                                Row.pop();
                            });
                        }
                        else {
                            this.ifElseBranchUpdateFunction(1, () => {
                            });
                        }
                    }, If);
                    If.pop();
                    // 结果卡片
                    Column.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Button.createWithLabel('完成');
                        Button.debugLine("entry/src/main/ets/pages/Checkin.ets(353:13)", "entry");
                        Button.width('70%');
                        Button.height(50);
                        Button.fontSize(18);
                        Button.fontColor('#FFFFFF');
                        Button.backgroundColor('#007DFF');
                        Button.borderRadius(10);
                        Button.onClick(() => {
                            this.handleFinish();
                        });
                    }, Button);
                    Button.pop();
                    // 结果展示
                    Column.pop();
                });
            }
            else {
                this.ifElseBranchUpdateFunction(3, () => {
                });
            }
        }, If);
        If.pop();
        // 主内容
        Column.pop();
        Column.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
    static getEntryName(): string {
        return "Checkin";
    }
}
registerNamedRoute(() => new Checkin(undefined, {}), "", { bundleName: "com.family.emotion", moduleName: "entry", pagePath: "pages/Checkin", pageFullPath: "entry/src/main/ets/pages/Checkin", integratedHsp: "false", moduleType: "followWithHap" });
