if (!("finalizeConstruction" in ViewPU.prototype)) {
    Reflect.set(ViewPU.prototype, "finalizeConstruction", () => { });
}
interface Index_Params {
    inviteCode?: string;
    isLoading?: boolean;
    message?: string;
}
import router from "@ohos:router";
import promptAction from "@ohos:promptAction";
import HttpUtil from "@bundle:com.family.emotion/entry/ets/common/utils/HttpUtil";
import StorageUtil from "@bundle:com.family.emotion/entry/ets/common/utils/StorageUtil";
import { ApiEndpoints, StorageKeys, AppConfig, ErrorMessages } from "@bundle:com.family.emotion/entry/ets/common/constants/AppConstants";
import type { LoginResponse } from '../models/User';
class Index extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.__inviteCode = new ObservedPropertySimplePU('', this, "inviteCode");
        this.__isLoading = new ObservedPropertySimplePU(false, this, "isLoading");
        this.__message = new ObservedPropertySimplePU('', this, "message");
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: Index_Params) {
        if (params.inviteCode !== undefined) {
            this.inviteCode = params.inviteCode;
        }
        if (params.isLoading !== undefined) {
            this.isLoading = params.isLoading;
        }
        if (params.message !== undefined) {
            this.message = params.message;
        }
    }
    updateStateVars(params: Index_Params) {
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
        this.__inviteCode.purgeDependencyOnElmtId(rmElmtId);
        this.__isLoading.purgeDependencyOnElmtId(rmElmtId);
        this.__message.purgeDependencyOnElmtId(rmElmtId);
    }
    aboutToBeDeleted() {
        this.__inviteCode.aboutToBeDeleted();
        this.__isLoading.aboutToBeDeleted();
        this.__message.aboutToBeDeleted();
        SubscriberManager.Get().delete(this.id__());
        this.aboutToBeDeletedInternal();
    }
    private __inviteCode: ObservedPropertySimplePU<string>;
    get inviteCode() {
        return this.__inviteCode.get();
    }
    set inviteCode(newValue: string) {
        this.__inviteCode.set(newValue);
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
    async aboutToAppear() {
        // 检查是否已保存邀请码,自动登录
        const savedInviteCode = await StorageUtil.getString(StorageKeys.INVITE_CODE);
        if (savedInviteCode) {
            this.inviteCode = savedInviteCode;
            console.info('[Index] Found saved invite code, auto login...');
            await this.handleLogin();
        }
    }
    /**
     * 处理登录
     */
    async handleLogin() {
        // 验证邀请码
        if (!this.inviteCode || this.inviteCode.trim().length === 0) {
            promptAction.showToast({
                message: '请输入邀请码',
                duration: 2000
            });
            return;
        }
        this.isLoading = true;
        this.message = '登录中...';
        try {
            // 调用邀请码登录API
            const requestBody: any = {
                'invite_code': this.inviteCode.trim().toUpperCase()
            };
            const response = await HttpUtil.post<LoginResponse>(ApiEndpoints.INVITE_LOGIN, requestBody, false // 登录时不需要Token
            );
            if (response.success && response.data) {
                // 保存登录信息
                await StorageUtil.setString(StorageKeys.INVITE_CODE, this.inviteCode.trim().toUpperCase());
                await StorageUtil.setString(StorageKeys.ACCESS_TOKEN, response.data.access);
                await StorageUtil.setString(StorageKeys.REFRESH_TOKEN, response.data.refresh);
                await StorageUtil.setObject(StorageKeys.USER_INFO, response.data.user);
                await StorageUtil.setBoolean(StorageKeys.IS_FACE_REGISTERED, response.data.user.face_registered);
                console.info('[Index] Login success, user:', JSON.stringify(response.data.user));
                // 显示欢迎消息
                promptAction.showToast({
                    message: `欢迎,${response.data.user.display_name}!`,
                    duration: 2000
                });
                // 登录流程到此结束,标记为成功
                this.isLoading = false;
                // 检查是否已注册人脸 - 在预览器中这个路由跳转会失败,但不影响登录本身
                const targetPage = !response.data.user.face_registered ?
                    AppConfig.PAGE_FACE_REGISTER : AppConfig.PAGE_HOME;
                console.info('[Index] Preparing to navigate to:', targetPage);
                // 延迟跳转,完全独立于登录流程
                setTimeout(() => {
                    router.replaceUrl({ url: targetPage })
                        .then(() => {
                        console.info('[Index] Navigation successful');
                    })
                        .catch((err: Error) => {
                        // 预览器不支持路由跳转,这是正常的
                        console.warn('[Index] Navigation failed (预览器限制):', JSON.stringify(err));
                    });
                }, 1000);
                return; // 提前返回,避免执行失败分支
            }
            else {
                // 登录失败
                this.message = response.error || ErrorMessages.LOGIN_FAILED;
                promptAction.showToast({
                    message: response.error || ErrorMessages.LOGIN_FAILED,
                    duration: 3000
                });
            }
        }
        catch (error) {
            console.error('[Index] Login error:', JSON.stringify(error));
            this.message = ErrorMessages.NETWORK_ERROR;
            promptAction.showToast({
                message: ErrorMessages.NETWORK_ERROR,
                duration: 3000
            });
        }
        finally {
            // 只有登录失败时才设置为false,成功时已经提前设置了
            if (this.isLoading) {
                this.isLoading = false;
            }
        }
    }
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create();
            Column.debugLine("entry/src/main/ets/pages/Index.ets(117:5)", "entry");
            Column.width('100%');
            Column.height('100%');
            Column.backgroundColor('#F5F5F5');
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 顶部Logo和标题
            Column.create();
            Column.debugLine("entry/src/main/ets/pages/Index.ets(119:7)", "entry");
            // 顶部Logo和标题
            Column.margin({ top: 80 });
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Image.create({ "id": 16777216, "type": 20000, params: [], "bundleName": "com.family.emotion", "moduleName": "entry" });
            Image.debugLine("entry/src/main/ets/pages/Index.ets(120:9)", "entry");
            Image.width(100);
            Image.height(100);
            Image.margin({ bottom: 20 });
        }, Image);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create(AppConfig.APP_NAME);
            Text.debugLine("entry/src/main/ets/pages/Index.ets(125:9)", "entry");
            Text.fontSize(28);
            Text.fontWeight(FontWeight.Bold);
            Text.fontColor('#333');
            Text.margin({ bottom: 10 });
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('用AI守护家人的心理健康');
            Text.debugLine("entry/src/main/ets/pages/Index.ets(131:9)", "entry");
            Text.fontSize(16);
            Text.fontColor('#666');
            Text.margin({ bottom: 40 });
        }, Text);
        Text.pop();
        // 顶部Logo和标题
        Column.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 邀请码输入区域
            Column.create();
            Column.debugLine("entry/src/main/ets/pages/Index.ets(139:7)", "entry");
            // 邀请码输入区域
            Column.width('85%');
            // 邀请码输入区域
            Column.padding({ left: 20, right: 20, top: 30, bottom: 30 });
            // 邀请码输入区域
            Column.backgroundColor('#FFFFFF');
            // 邀请码输入区域
            Column.borderRadius(15);
            // 邀请码输入区域
            Column.shadow({
                radius: 20,
                color: '#00000010',
                offsetX: 0,
                offsetY: 5
            });
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('请输入邀请码');
            Text.debugLine("entry/src/main/ets/pages/Index.ets(140:9)", "entry");
            Text.fontSize(18);
            Text.fontWeight(FontWeight.Medium);
            Text.fontColor('#333');
            Text.alignSelf(ItemAlign.Start);
            Text.margin({ bottom: 15 });
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            TextInput.create({ placeholder: '请输入8位邀请码', text: this.inviteCode });
            TextInput.debugLine("entry/src/main/ets/pages/Index.ets(147:9)", "entry");
            TextInput.height(50);
            TextInput.fontSize(16);
            TextInput.maxLength(8);
            TextInput.type(InputType.Normal);
            TextInput.placeholderColor('#999');
            TextInput.backgroundColor('#F5F5F5');
            TextInput.borderRadius(10);
            TextInput.padding({ left: 15, right: 15 });
            TextInput.onChange((value: string) => {
                this.inviteCode = value.toUpperCase();
            });
            TextInput.margin({ bottom: 20 });
        }, TextInput);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 登录按钮
            Button.createWithLabel(this.isLoading ? '登录中...' : '登录');
            Button.debugLine("entry/src/main/ets/pages/Index.ets(162:9)", "entry");
            // 登录按钮
            Button.width('100%');
            // 登录按钮
            Button.height(50);
            // 登录按钮
            Button.fontSize(18);
            // 登录按钮
            Button.fontColor('#FFFFFF');
            // 登录按钮
            Button.backgroundColor(this.isLoading ? '#CCCCCC' : '#007DFF');
            // 登录按钮
            Button.borderRadius(10);
            // 登录按钮
            Button.enabled(!this.isLoading);
            // 登录按钮
            Button.onClick(() => {
                this.handleLogin();
            });
        }, Button);
        // 登录按钮
        Button.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            If.create();
            // 提示信息
            if (this.message) {
                this.ifElseBranchUpdateFunction(0, () => {
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create(this.message);
                        Text.debugLine("entry/src/main/ets/pages/Index.ets(176:11)", "entry");
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
        // 邀请码输入区域
        Column.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 说明文字
            Column.create();
            Column.debugLine("entry/src/main/ets/pages/Index.ets(194:7)", "entry");
            // 说明文字
            Column.margin({ top: 40 });
            // 说明文字
            Column.padding(20);
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('如何获取邀请码?');
            Text.debugLine("entry/src/main/ets/pages/Index.ets(195:9)", "entry");
            Text.fontSize(16);
            Text.fontWeight(FontWeight.Medium);
            Text.fontColor('#333');
            Text.margin({ bottom: 10 });
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('1. 请联系家庭管理员');
            Text.debugLine("entry/src/main/ets/pages/Index.ets(201:9)", "entry");
            Text.fontSize(14);
            Text.fontColor('#666');
            Text.margin({ bottom: 5 });
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('2. 管理员在Web管理界面生成邀请码');
            Text.debugLine("entry/src/main/ets/pages/Index.ets(206:9)", "entry");
            Text.fontSize(14);
            Text.fontColor('#666');
            Text.margin({ bottom: 5 });
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('3. 使用邀请码即可登录');
            Text.debugLine("entry/src/main/ets/pages/Index.ets(211:9)", "entry");
            Text.fontSize(14);
            Text.fontColor('#666');
        }, Text);
        Text.pop();
        // 说明文字
        Column.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Blank.create();
            Blank.debugLine("entry/src/main/ets/pages/Index.ets(218:7)", "entry");
        }, Blank);
        Blank.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 底部版本信息
            Text.create(`版本 ${AppConfig.APP_VERSION}`);
            Text.debugLine("entry/src/main/ets/pages/Index.ets(221:7)", "entry");
            // 底部版本信息
            Text.fontSize(12);
            // 底部版本信息
            Text.fontColor('#999');
            // 底部版本信息
            Text.margin({ bottom: 20 });
        }, Text);
        // 底部版本信息
        Text.pop();
        Column.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
    static getEntryName(): string {
        return "Index";
    }
}
registerNamedRoute(() => new Index(undefined, {}), "", { bundleName: "com.family.emotion", moduleName: "entry", pagePath: "pages/Index", pageFullPath: "entry/src/main/ets/pages/Index", integratedHsp: "false", moduleType: "followWithHap" });
