if (!("finalizeConstruction" in ViewPU.prototype)) {
    Reflect.set(ViewPU.prototype, "finalizeConstruction", () => { });
}
interface History_Params {
    records?: CheckinRecord[];
    isLoading?: boolean;
    isRefreshing?: boolean;
    hasMore?: boolean;
    page?: number;
}
import router from "@ohos:router";
import promptAction from "@ohos:promptAction";
import HttpUtil from "@bundle:com.family.emotion/entry/ets/common/utils/HttpUtil";
import { ApiEndpoints, EMOTION_NAMES, ErrorMessages } from "@bundle:com.family.emotion/entry/ets/common/constants/AppConstants";
import type { CheckinRecordListResponse, CheckinRecord } from '../models/CheckinRecord';
class History extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.__records = new ObservedPropertyObjectPU([], this, "records");
        this.__isLoading = new ObservedPropertySimplePU(false, this, "isLoading");
        this.__isRefreshing = new ObservedPropertySimplePU(false, this, "isRefreshing");
        this.__hasMore = new ObservedPropertySimplePU(true, this, "hasMore");
        this.__page = new ObservedPropertySimplePU(1, this, "page");
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: History_Params) {
        if (params.records !== undefined) {
            this.records = params.records;
        }
        if (params.isLoading !== undefined) {
            this.isLoading = params.isLoading;
        }
        if (params.isRefreshing !== undefined) {
            this.isRefreshing = params.isRefreshing;
        }
        if (params.hasMore !== undefined) {
            this.hasMore = params.hasMore;
        }
        if (params.page !== undefined) {
            this.page = params.page;
        }
    }
    updateStateVars(params: History_Params) {
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
        this.__records.purgeDependencyOnElmtId(rmElmtId);
        this.__isLoading.purgeDependencyOnElmtId(rmElmtId);
        this.__isRefreshing.purgeDependencyOnElmtId(rmElmtId);
        this.__hasMore.purgeDependencyOnElmtId(rmElmtId);
        this.__page.purgeDependencyOnElmtId(rmElmtId);
    }
    aboutToBeDeleted() {
        this.__records.aboutToBeDeleted();
        this.__isLoading.aboutToBeDeleted();
        this.__isRefreshing.aboutToBeDeleted();
        this.__hasMore.aboutToBeDeleted();
        this.__page.aboutToBeDeleted();
        SubscriberManager.Get().delete(this.id__());
        this.aboutToBeDeletedInternal();
    }
    private __records: ObservedPropertyObjectPU<CheckinRecord[]>;
    get records() {
        return this.__records.get();
    }
    set records(newValue: CheckinRecord[]) {
        this.__records.set(newValue);
    }
    private __isLoading: ObservedPropertySimplePU<boolean>;
    get isLoading() {
        return this.__isLoading.get();
    }
    set isLoading(newValue: boolean) {
        this.__isLoading.set(newValue);
    }
    private __isRefreshing: ObservedPropertySimplePU<boolean>;
    get isRefreshing() {
        return this.__isRefreshing.get();
    }
    set isRefreshing(newValue: boolean) {
        this.__isRefreshing.set(newValue);
    }
    private __hasMore: ObservedPropertySimplePU<boolean>;
    get hasMore() {
        return this.__hasMore.get();
    }
    set hasMore(newValue: boolean) {
        this.__hasMore.set(newValue);
    }
    private __page: ObservedPropertySimplePU<number>;
    get page() {
        return this.__page.get();
    }
    set page(newValue: number) {
        this.__page.set(newValue);
    }
    async aboutToAppear() {
        await this.loadRecords();
    }
    /**
     * 加载打卡记录
     */
    async loadRecords(refresh: boolean = false) {
        if (refresh) {
            this.isRefreshing = true;
            this.page = 1;
            this.records = [];
        }
        else {
            this.isLoading = true;
        }
        try {
            const url = `${ApiEndpoints.CHECKIN_RECORDS}?page=${this.page}&page_size=20`;
            const response = await HttpUtil.get<CheckinRecordListResponse>(url);
            if (response.success && response.data) {
                if (refresh) {
                    this.records = response.data.results;
                }
                else {
                    this.records = [...this.records, ...response.data.results];
                }
                this.hasMore = !!response.data.next;
                console.info(`[History] Loaded ${response.data.results.length} records`);
            }
            else {
                promptAction.showToast({
                    message: response.error || '加载失败',
                    duration: 2000
                });
            }
        }
        catch (error) {
            console.error('[History] Load records error:', JSON.stringify(error));
            promptAction.showToast({
                message: ErrorMessages.NETWORK_ERROR,
                duration: 2000
            });
        }
        finally {
            this.isLoading = false;
            this.isRefreshing = false;
        }
    }
    /**
     * 加载更多
     */
    async loadMore() {
        if (this.isLoading || !this.hasMore) {
            return;
        }
        this.page++;
        await this.loadRecords();
    }
    /**
     * 下拉刷新
     */
    async handleRefresh() {
        await this.loadRecords(true);
    }
    /**
     * 格式化日期时间
     */
    formatDateTime(dateString: string): string {
        const date = new Date(dateString);
        const month = date.getMonth() + 1;
        const day = date.getDate();
        const hour = date.getHours();
        const minute = date.getMinutes();
        return `${month}月${day}日 ${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
    }
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create();
            Column.debugLine("entry/src/main/ets/pages/History.ets(98:5)", "entry");
            Column.width('100%');
            Column.height('100%');
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 顶部标题栏
            Row.create();
            Row.debugLine("entry/src/main/ets/pages/History.ets(100:7)", "entry");
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
            Image.debugLine("entry/src/main/ets/pages/History.ets(101:9)", "entry");
            Image.width(24);
            Image.height(24);
            Image.onClick(() => {
                router.back();
            });
        }, Image);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('历史记录');
            Text.debugLine("entry/src/main/ets/pages/History.ets(108:9)", "entry");
            Text.fontSize(20);
            Text.fontWeight(FontWeight.Medium);
            Text.fontColor('#333');
            Text.layoutWeight(1);
            Text.textAlign(TextAlign.Center);
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 占位
            Column.create();
            Column.debugLine("entry/src/main/ets/pages/History.ets(116:9)", "entry");
            // 占位
            Column.width(24);
            // 占位
            Column.height(24);
        }, Column);
        // 占位
        Column.pop();
        // 顶部标题栏
        Row.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            If.create();
            // 记录列表
            if (this.records.length > 0) {
                this.ifElseBranchUpdateFunction(0, () => {
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        List.create();
                        List.debugLine("entry/src/main/ets/pages/History.ets(127:9)", "entry");
                        List.width('100%');
                        List.layoutWeight(1);
                        List.backgroundColor('#F5F5F5');
                        List.edgeEffect(EdgeEffect.Spring);
                        List.onReachEnd(() => {
                            this.loadMore();
                        });
                        List.onScrollFrameBegin((offset: number) => {
                            // 下拉刷新逻辑(简化版)
                            if (offset < -100 && !this.isRefreshing && !this.isLoading) {
                                this.handleRefresh();
                            }
                            return { offsetRemain: offset };
                        });
                    }, List);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        ForEach.create();
                        const forEachItemGenFunction = _item => {
                            const record = _item;
                            {
                                const itemCreation = (elmtId, isInitialRender) => {
                                    ViewStackProcessor.StartGetAccessRecordingFor(elmtId);
                                    ListItem.create(deepRenderFunction, true);
                                    if (!isInitialRender) {
                                        ListItem.pop();
                                    }
                                    ViewStackProcessor.StopGetAccessRecording();
                                };
                                const itemCreation2 = (elmtId, isInitialRender) => {
                                    ListItem.create(deepRenderFunction, true);
                                    ListItem.debugLine("entry/src/main/ets/pages/History.ets(129:13)", "entry");
                                };
                                const deepRenderFunction = (elmtId, isInitialRender) => {
                                    itemCreation(elmtId, isInitialRender);
                                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                                        Column.create();
                                        Column.debugLine("entry/src/main/ets/pages/History.ets(130:15)", "entry");
                                        Column.width('95%');
                                        Column.backgroundColor('#FFFFFF');
                                        Column.borderRadius(10);
                                        Column.margin({ top: 10, left: 10, right: 10 });
                                        Column.shadow({
                                            radius: 8,
                                            color: '#00000008',
                                            offsetX: 0,
                                            offsetY: 2
                                        });
                                    }, Column);
                                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                                        Row.create();
                                        Row.debugLine("entry/src/main/ets/pages/History.ets(131:17)", "entry");
                                        Row.width('100%');
                                        Row.padding(20);
                                    }, Row);
                                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                                        // 左侧:日期时间
                                        Column.create();
                                        Column.debugLine("entry/src/main/ets/pages/History.ets(133:19)", "entry");
                                        // 左侧:日期时间
                                        Column.alignItems(HorizontalAlign.Start);
                                    }, Column);
                                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                                        Text.create(this.formatDateTime(record.checkin_time));
                                        Text.debugLine("entry/src/main/ets/pages/History.ets(134:21)", "entry");
                                        Text.fontSize(16);
                                        Text.fontColor('#333');
                                        Text.fontWeight(FontWeight.Medium);
                                        Text.margin({ bottom: 5 });
                                    }, Text);
                                    Text.pop();
                                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                                        Text.create(record.task ? `任务ID: ${record.task}` : '');
                                        Text.debugLine("entry/src/main/ets/pages/History.ets(140:21)", "entry");
                                        Text.fontSize(14);
                                        Text.fontColor('#999');
                                    }, Text);
                                    Text.pop();
                                    // 左侧:日期时间
                                    Column.pop();
                                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                                        Blank.create();
                                        Blank.debugLine("entry/src/main/ets/pages/History.ets(146:19)", "entry");
                                    }, Blank);
                                    Blank.pop();
                                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                                        // 右侧:状态和情绪
                                        Column.create();
                                        Column.debugLine("entry/src/main/ets/pages/History.ets(149:19)", "entry");
                                        // 右侧:状态和情绪
                                        Column.alignItems(HorizontalAlign.End);
                                    }, Column);
                                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                                        // 打卡状态
                                        Text.create(record.status === 'on_time' ? '✓ 准时' :
                                            record.status === 'late' ? '⚠ 迟到' : '补签');
                                        Text.debugLine("entry/src/main/ets/pages/History.ets(151:21)", "entry");
                                        // 打卡状态
                                        Text.fontSize(14);
                                        // 打卡状态
                                        Text.fontColor(record.status === 'on_time' ? '#52C41A' :
                                            record.status === 'late' ? '#FAAD14' : '#F5222D');
                                        // 打卡状态
                                        Text.fontWeight(FontWeight.Medium);
                                        // 打卡状态
                                        Text.margin({ bottom: 8 });
                                    }, Text);
                                    // 打卡状态
                                    Text.pop();
                                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                                        If.create();
                                        // 情绪
                                        if (record.emotion) {
                                            this.ifElseBranchUpdateFunction(0, () => {
                                                this.observeComponentCreation2((elmtId, isInitialRender) => {
                                                    Text.create(EMOTION_NAMES[record.emotion] || record.emotion);
                                                    Text.debugLine("entry/src/main/ets/pages/History.ets(165:23)", "entry");
                                                    Text.fontSize(20);
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
                                    // 右侧:状态和情绪
                                    Column.pop();
                                    Row.pop();
                                    Column.pop();
                                    ListItem.pop();
                                };
                                this.observeComponentCreation2(itemCreation2, ListItem);
                                ListItem.pop();
                            }
                        };
                        this.forEachUpdateFunction(elmtId, this.records, forEachItemGenFunction);
                    }, ForEach);
                    ForEach.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        If.create();
                        // 加载更多指示器
                        if (this.hasMore) {
                            this.ifElseBranchUpdateFunction(0, () => {
                                {
                                    const itemCreation = (elmtId, isInitialRender) => {
                                        ViewStackProcessor.StartGetAccessRecordingFor(elmtId);
                                        ListItem.create(deepRenderFunction, true);
                                        if (!isInitialRender) {
                                            ListItem.pop();
                                        }
                                        ViewStackProcessor.StopGetAccessRecording();
                                    };
                                    const itemCreation2 = (elmtId, isInitialRender) => {
                                        ListItem.create(deepRenderFunction, true);
                                        ListItem.onClick(() => {
                                            this.loadMore();
                                        });
                                        ListItem.debugLine("entry/src/main/ets/pages/History.ets(189:13)", "entry");
                                    };
                                    const deepRenderFunction = (elmtId, isInitialRender) => {
                                        itemCreation(elmtId, isInitialRender);
                                        this.observeComponentCreation2((elmtId, isInitialRender) => {
                                            Row.create();
                                            Row.debugLine("entry/src/main/ets/pages/History.ets(190:15)", "entry");
                                            Row.width('100%');
                                            Row.height(60);
                                            Row.justifyContent(FlexAlign.Center);
                                        }, Row);
                                        this.observeComponentCreation2((elmtId, isInitialRender) => {
                                            If.create();
                                            if (this.isLoading) {
                                                this.ifElseBranchUpdateFunction(0, () => {
                                                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                                                        LoadingProgress.create();
                                                        LoadingProgress.debugLine("entry/src/main/ets/pages/History.ets(192:19)", "entry");
                                                        LoadingProgress.width(30);
                                                        LoadingProgress.height(30);
                                                        LoadingProgress.margin({ right: 10 });
                                                    }, LoadingProgress);
                                                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                                                        Text.create('加载中...');
                                                        Text.debugLine("entry/src/main/ets/pages/History.ets(196:19)", "entry");
                                                        Text.fontSize(14);
                                                        Text.fontColor('#999');
                                                    }, Text);
                                                    Text.pop();
                                                });
                                            }
                                            else {
                                                this.ifElseBranchUpdateFunction(1, () => {
                                                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                                                        Text.create('上拉加载更多');
                                                        Text.debugLine("entry/src/main/ets/pages/History.ets(200:19)", "entry");
                                                        Text.fontSize(14);
                                                        Text.fontColor('#999');
                                                    }, Text);
                                                    Text.pop();
                                                });
                                            }
                                        }, If);
                                        If.pop();
                                        Row.pop();
                                        ListItem.pop();
                                    };
                                    this.observeComponentCreation2(itemCreation2, ListItem);
                                    ListItem.pop();
                                }
                            });
                        }
                        else {
                            this.ifElseBranchUpdateFunction(1, () => {
                                {
                                    const itemCreation = (elmtId, isInitialRender) => {
                                        ViewStackProcessor.StartGetAccessRecordingFor(elmtId);
                                        ListItem.create(deepRenderFunction, true);
                                        if (!isInitialRender) {
                                            ListItem.pop();
                                        }
                                        ViewStackProcessor.StopGetAccessRecording();
                                    };
                                    const itemCreation2 = (elmtId, isInitialRender) => {
                                        ListItem.create(deepRenderFunction, true);
                                        ListItem.debugLine("entry/src/main/ets/pages/History.ets(213:13)", "entry");
                                    };
                                    const deepRenderFunction = (elmtId, isInitialRender) => {
                                        itemCreation(elmtId, isInitialRender);
                                        this.observeComponentCreation2((elmtId, isInitialRender) => {
                                            Text.create('没有更多了');
                                            Text.debugLine("entry/src/main/ets/pages/History.ets(214:15)", "entry");
                                            Text.fontSize(14);
                                            Text.fontColor('#999');
                                            Text.width('100%');
                                            Text.height(60);
                                            Text.textAlign(TextAlign.Center);
                                        }, Text);
                                        Text.pop();
                                        ListItem.pop();
                                    };
                                    this.observeComponentCreation2(itemCreation2, ListItem);
                                    ListItem.pop();
                                }
                            });
                        }
                    }, If);
                    If.pop();
                    List.pop();
                });
            }
            else if (this.isLoading) {
                this.ifElseBranchUpdateFunction(1, () => {
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        // 首次加载
                        Column.create();
                        Column.debugLine("entry/src/main/ets/pages/History.ets(240:9)", "entry");
                        // 首次加载
                        Column.width('100%');
                        // 首次加载
                        Column.layoutWeight(1);
                        // 首次加载
                        Column.justifyContent(FlexAlign.Center);
                        // 首次加载
                        Column.backgroundColor('#F5F5F5');
                    }, Column);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        LoadingProgress.create();
                        LoadingProgress.debugLine("entry/src/main/ets/pages/History.ets(241:11)", "entry");
                        LoadingProgress.width(50);
                        LoadingProgress.height(50);
                        LoadingProgress.margin({ bottom: 20 });
                    }, LoadingProgress);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create('加载中...');
                        Text.debugLine("entry/src/main/ets/pages/History.ets(246:11)", "entry");
                        Text.fontSize(16);
                        Text.fontColor('#999');
                    }, Text);
                    Text.pop();
                    // 首次加载
                    Column.pop();
                });
            }
            else {
                this.ifElseBranchUpdateFunction(2, () => {
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        // 空状态
                        Column.create();
                        Column.debugLine("entry/src/main/ets/pages/History.ets(257:9)", "entry");
                        // 空状态
                        Column.width('100%');
                        // 空状态
                        Column.layoutWeight(1);
                        // 空状态
                        Column.justifyContent(FlexAlign.Center);
                        // 空状态
                        Column.backgroundColor('#F5F5F5');
                    }, Column);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Image.create($r('app.media.empty'));
                        Image.debugLine("entry/src/main/ets/pages/History.ets(258:11)", "entry");
                        Image.width(150);
                        Image.height(150);
                        Image.margin({ bottom: 20 });
                    }, Image);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create('暂无打卡记录');
                        Text.debugLine("entry/src/main/ets/pages/History.ets(263:11)", "entry");
                        Text.fontSize(18);
                        Text.fontColor('#999');
                        Text.margin({ bottom: 10 });
                    }, Text);
                    Text.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create('完成首次打卡后,记录将显示在这里');
                        Text.debugLine("entry/src/main/ets/pages/History.ets(268:11)", "entry");
                        Text.fontSize(14);
                        Text.fontColor('#CCCCCC');
                    }, Text);
                    Text.pop();
                    // 空状态
                    Column.pop();
                });
            }
        }, If);
        If.pop();
        Column.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
    static getEntryName(): string {
        return "History";
    }
}
registerNamedRoute(() => new History(undefined, {}), "", { bundleName: "com.family.emotion", moduleName: "entry", pagePath: "pages/History", pageFullPath: "entry/src/main/ets/pages/History", integratedHsp: "false", moduleType: "followWithHap" });
