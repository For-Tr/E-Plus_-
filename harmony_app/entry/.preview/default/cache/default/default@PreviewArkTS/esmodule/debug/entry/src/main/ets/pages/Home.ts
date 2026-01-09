if (!("finalizeConstruction" in ViewPU.prototype)) {
    Reflect.set(ViewPU.prototype, "finalizeConstruction", () => { });
}
interface Home_Params {
    user?: User | null;
    isLoading?: boolean;
    hasActiveTasks?: boolean;
}
import router from "@ohos:router";
import promptAction from "@ohos:promptAction";
import HttpUtil from "@bundle:com.family.emotion/entry/ets/common/utils/HttpUtil";
import StorageUtil from "@bundle:com.family.emotion/entry/ets/common/utils/StorageUtil";
import { ApiEndpoints, StorageKeys, AppConfig } from "@bundle:com.family.emotion/entry/ets/common/constants/AppConstants";
import type { User } from '../models/User';
import type { CheckinTaskListResponse } from '../models/CheckinTask';
class Home extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.__user = new ObservedPropertyObjectPU(null, this, "user");
        this.__isLoading = new ObservedPropertySimplePU(false, this, "isLoading");
        this.__hasActiveTasks = new ObservedPropertySimplePU(false, this, "hasActiveTasks");
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: Home_Params) {
        if (params.user !== undefined) {
            this.user = params.user;
        }
        if (params.isLoading !== undefined) {
            this.isLoading = params.isLoading;
        }
        if (params.hasActiveTasks !== undefined) {
            this.hasActiveTasks = params.hasActiveTasks;
        }
    }
    updateStateVars(params: Home_Params) {
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
        this.__user.purgeDependencyOnElmtId(rmElmtId);
        this.__isLoading.purgeDependencyOnElmtId(rmElmtId);
        this.__hasActiveTasks.purgeDependencyOnElmtId(rmElmtId);
    }
    aboutToBeDeleted() {
        this.__user.aboutToBeDeleted();
        this.__isLoading.aboutToBeDeleted();
        this.__hasActiveTasks.aboutToBeDeleted();
        SubscriberManager.Get().delete(this.id__());
        this.aboutToBeDeletedInternal();
    }
    private __user: ObservedPropertyObjectPU<User | null>;
    get user() {
        return this.__user.get();
    }
    set user(newValue: User | null) {
        this.__user.set(newValue);
    }
    private __isLoading: ObservedPropertySimplePU<boolean>;
    get isLoading() {
        return this.__isLoading.get();
    }
    set isLoading(newValue: boolean) {
        this.__isLoading.set(newValue);
    }
    private __hasActiveTasks: ObservedPropertySimplePU<boolean>;
    get hasActiveTasks() {
        return this.__hasActiveTasks.get();
    }
    set hasActiveTasks(newValue: boolean) {
        this.__hasActiveTasks.set(newValue);
    }
    async aboutToAppear() {
        await this.loadUserInfo();
        await this.checkTasks();
    }
    /**
     * 加载用户信息
     */
    async loadUserInfo() {
        const userInfo = await StorageUtil.getObject(StorageKeys.USER_INFO);
        if (userInfo) {
            this.user = userInfo as User;
            console.info('[Home] User loaded:', JSON.stringify(this.user));
        }
    }
    /**
     * 检查是否有活跃的打卡任务
     */
    async checkTasks() {
        try {
            const response = await HttpUtil.get<CheckinTaskListResponse>(ApiEndpoints.CHECKIN_TASKS);
            if (response.success && response.data) {
                this.hasActiveTasks = response.data.results.length > 0;
                console.info(`[Home] Active tasks count: ${response.data.results.length}`);
            }
        }
        catch (error) {
            console.error('[Home] Check tasks error:', JSON.stringify(error));
        }
    }
    /**
     * 开始打卡
     */
    handleStartCheckin() {
        if (!this.hasActiveTasks) {
            promptAction.showToast({
                message: '暂无打卡任务',
                duration: 2000
            });
            return;
        }
        router.pushUrl({
            url: AppConfig.PAGE_CHECKIN
        });
    }
    /**
     * 查看历史记录
     */
    handleViewHistory() {
        router.pushUrl({
            url: AppConfig.PAGE_HISTORY
        });
    }
    /**
     * 退出登录
     */
    async handleLogout() {
        try {
            // 清除本地存储
            await StorageUtil.clear();
            promptAction.showToast({
                message: '已退出登录',
                duration: 2000
            });
            // 返回登录页
            router.replaceUrl({
                url: AppConfig.PAGE_INDEX
            });
        }
        catch (error) {
            console.error('[Home] Logout error:', JSON.stringify(error));
        }
    }
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create();
            Column.debugLine("entry/src/main/ets/pages/Home.ets(99:5)", "entry");
            Column.width('100%');
            Column.height('100%');
            Column.backgroundColor('#F5F5F5');
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 顶部用户信息栏
            Row.create();
            Row.debugLine("entry/src/main/ets/pages/Home.ets(101:7)", "entry");
            // 顶部用户信息栏
            Row.width('100%');
            // 顶部用户信息栏
            Row.padding(20);
            // 顶部用户信息栏
            Row.backgroundColor('#FFFFFF');
        }, Row);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 用户头像
            Image.create({ "id": 16777233, "type": 20000, params: [], "bundleName": "com.family.emotion", "moduleName": "entry" });
            Image.debugLine("entry/src/main/ets/pages/Home.ets(103:9)", "entry");
            // 用户头像
            Image.width(50);
            // 用户头像
            Image.height(50);
            // 用户头像
            Image.borderRadius(25);
            // 用户头像
            Image.margin({ right: 15 });
        }, Image);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 用户信息
            Column.create();
            Column.debugLine("entry/src/main/ets/pages/Home.ets(110:9)", "entry");
            // 用户信息
            Column.alignItems(HorizontalAlign.Start);
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create(this.user?.display_name || '用户');
            Text.debugLine("entry/src/main/ets/pages/Home.ets(111:11)", "entry");
            Text.fontSize(18);
            Text.fontWeight(FontWeight.Medium);
            Text.fontColor('#333');
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create(this.user?.family?.name || '未加入家庭');
            Text.debugLine("entry/src/main/ets/pages/Home.ets(116:11)", "entry");
            Text.fontSize(14);
            Text.fontColor('#999');
            Text.margin({ top: 5 });
        }, Text);
        Text.pop();
        // 用户信息
        Column.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Blank.create();
            Blank.debugLine("entry/src/main/ets/pages/Home.ets(123:9)", "entry");
        }, Blank);
        Blank.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 退出按钮
            Button.createWithLabel('退出');
            Button.debugLine("entry/src/main/ets/pages/Home.ets(126:9)", "entry");
            // 退出按钮
            Button.fontSize(14);
            // 退出按钮
            Button.fontColor('#FF0000');
            // 退出按钮
            Button.backgroundColor('#FFFFFF');
            // 退出按钮
            Button.border({ width: 1, color: '#FF0000' });
            // 退出按钮
            Button.borderRadius(5);
            // 退出按钮
            Button.padding({ left: 15, right: 15, top: 8, bottom: 8 });
            // 退出按钮
            Button.onClick(() => {
                this.handleLogout();
            });
        }, Button);
        // 退出按钮
        Button.pop();
        // 顶部用户信息栏
        Row.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 主内容区域
            Column.create();
            Column.debugLine("entry/src/main/ets/pages/Home.ets(142:7)", "entry");
            // 主内容区域
            Column.width('100%');
            // 主内容区域
            Column.layoutWeight(1);
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 打卡按钮
            Column.create();
            Column.debugLine("entry/src/main/ets/pages/Home.ets(144:9)", "entry");
            // 打卡按钮
            Column.width('85%');
            // 打卡按钮
            Column.padding(40);
            // 打卡按钮
            Column.backgroundColor(this.hasActiveTasks ? '#007DFF' : '#CCCCCC');
            // 打卡按钮
            Column.borderRadius(20);
            // 打卡按钮
            Column.shadow({
                radius: 20,
                color: '#00000020',
                offsetX: 0,
                offsetY: 5
            });
            // 打卡按钮
            Column.onClick(() => {
                this.handleStartCheckin();
            });
            // 打卡按钮
            Column.margin({ top: 40 });
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Image.create({ "id": 16777232, "type": 20000, params: [], "bundleName": "com.family.emotion", "moduleName": "entry" });
            Image.debugLine("entry/src/main/ets/pages/Home.ets(145:11)", "entry");
            Image.width(80);
            Image.height(80);
            Image.margin({ bottom: 20 });
        }, Image);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('开始打卡');
            Text.debugLine("entry/src/main/ets/pages/Home.ets(150:11)", "entry");
            Text.fontSize(24);
            Text.fontWeight(FontWeight.Bold);
            Text.fontColor('#FFFFFF');
            Text.margin({ bottom: 10 });
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create(this.hasActiveTasks ? '点击进行打卡' : '暂无打卡任务');
            Text.debugLine("entry/src/main/ets/pages/Home.ets(156:11)", "entry");
            Text.fontSize(14);
            Text.fontColor('#FFFFFF');
            Text.opacity(0.8);
        }, Text);
        Text.pop();
        // 打卡按钮
        Column.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 功能按钮组
            Row.create();
            Row.debugLine("entry/src/main/ets/pages/Home.ets(177:9)", "entry");
            // 功能按钮组
            Row.width('85%');
            // 功能按钮组
            Row.margin({ top: 30 });
        }, Row);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 历史记录
            Column.create();
            Column.debugLine("entry/src/main/ets/pages/Home.ets(179:11)", "entry");
            // 历史记录
            Column.width('45%');
            // 历史记录
            Column.padding(20);
            // 历史记录
            Column.backgroundColor('#FFFFFF');
            // 历史记录
            Column.borderRadius(15);
            // 历史记录
            Column.shadow({
                radius: 10,
                color: '#00000010',
                offsetX: 0,
                offsetY: 2
            });
            // 历史记录
            Column.onClick(() => {
                this.handleViewHistory();
            });
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Image.create({ "id": 16777228, "type": 20000, params: [], "bundleName": "com.family.emotion", "moduleName": "entry" });
            Image.debugLine("entry/src/main/ets/pages/Home.ets(180:13)", "entry");
            Image.width(40);
            Image.height(40);
            Image.margin({ bottom: 10 });
        }, Image);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('历史记录');
            Text.debugLine("entry/src/main/ets/pages/Home.ets(185:13)", "entry");
            Text.fontSize(14);
            Text.fontColor('#666');
        }, Text);
        Text.pop();
        // 历史记录
        Column.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Blank.create();
            Blank.debugLine("entry/src/main/ets/pages/Home.ets(203:11)", "entry");
        }, Blank);
        Blank.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 人脸管理
            Column.create();
            Column.debugLine("entry/src/main/ets/pages/Home.ets(206:11)", "entry");
            // 人脸管理
            Column.width('45%');
            // 人脸管理
            Column.padding(20);
            // 人脸管理
            Column.backgroundColor('#FFFFFF');
            // 人脸管理
            Column.borderRadius(15);
            // 人脸管理
            Column.shadow({
                radius: 10,
                color: '#00000010',
                offsetX: 0,
                offsetY: 2
            });
            // 人脸管理
            Column.onClick(() => {
                router.pushUrl({
                    url: AppConfig.PAGE_FACE_REGISTER
                });
            });
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Image.create({ "id": 16777234, "type": 20000, params: [], "bundleName": "com.family.emotion", "moduleName": "entry" });
            Image.debugLine("entry/src/main/ets/pages/Home.ets(207:13)", "entry");
            Image.width(40);
            Image.height(40);
            Image.margin({ bottom: 10 });
        }, Image);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('人脸管理');
            Text.debugLine("entry/src/main/ets/pages/Home.ets(212:13)", "entry");
            Text.fontSize(14);
            Text.fontColor('#666');
        }, Text);
        Text.pop();
        // 人脸管理
        Column.pop();
        // 功能按钮组
        Row.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 提示信息
            Column.create();
            Column.debugLine("entry/src/main/ets/pages/Home.ets(236:9)", "entry");
            // 提示信息
            Column.width('85%');
            // 提示信息
            Column.padding(20);
            // 提示信息
            Column.backgroundColor('#FFF9E6');
            // 提示信息
            Column.borderRadius(10);
            // 提示信息
            Column.margin({ top: 30 });
            // 提示信息
            Column.alignItems(HorizontalAlign.Start);
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('使用说明');
            Text.debugLine("entry/src/main/ets/pages/Home.ets(237:11)", "entry");
            Text.fontSize(16);
            Text.fontWeight(FontWeight.Medium);
            Text.fontColor('#333');
            Text.margin({ bottom: 10 });
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('• 每日按时打卡,记录您的情绪状态');
            Text.debugLine("entry/src/main/ets/pages/Home.ets(243:11)", "entry");
            Text.fontSize(14);
            Text.fontColor('#666');
            Text.margin({ bottom: 5 });
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('• 打卡时会自动识别您的表情');
            Text.debugLine("entry/src/main/ets/pages/Home.ets(248:11)", "entry");
            Text.fontSize(14);
            Text.fontColor('#666');
            Text.margin({ bottom: 5 });
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('• 家庭管理员可查看所有成员的情绪记录');
            Text.debugLine("entry/src/main/ets/pages/Home.ets(253:11)", "entry");
            Text.fontSize(14);
            Text.fontColor('#666');
        }, Text);
        Text.pop();
        // 提示信息
        Column.pop();
        // 主内容区域
        Column.pop();
        Column.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
    static getEntryName(): string {
        return "Home";
    }
}
registerNamedRoute(() => new Home(undefined, {}), "", { bundleName: "com.family.emotion", moduleName: "entry", pagePath: "pages/Home", pageFullPath: "entry/src/main/ets/pages/Home", integratedHsp: "false", moduleType: "followWithHap" });
