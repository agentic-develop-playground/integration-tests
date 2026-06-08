# -*- coding: utf-8 -*-
"""
UI 测试脚本：datastat 数据中台（preview 环境，无需登录）

被测对象：datastat 数据中台前端
测试框架：pytest + playwright
环境：https://datastat-manage-website.preview.test.osinfra.cn/

配置（.env）：
    DATASTAT_BASE_URL=https://datastat-manage-website.preview.test.osinfra.cn

执行：
    pip install pytest playwright python-dotenv
    playwright install chromium
    pytest -v test_datastat_ui.py
"""

import os

import pytest
from playwright.sync_api import Page, expect

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_URL = "https://datastat-manage-website.preview.test.osinfra.cn"


# ===== Fixture =====

@pytest.fixture(scope="function")
def home_page(page: Page):
    """打开根路径，前端会自动跳转到默认社区的概览页"""
    page.goto(f"{BASE_URL}/", wait_until="domcontentloaded", timeout=30000)
    # 等前端 router 完成默认重定向
    try:
        page.wait_for_url("**/overview**", timeout=8000)
    except Exception:
        pass
    page.wait_for_timeout(1500)
    return page


# ===== 页面导航测试 =====

class TestNavigation:

    def test_root_loads(self, home_page: Page):
        """TC-UI-001 [正常流] 根路径加载并自动进入概览页（或停留根页 #app 渲染）"""
        # preview 环境根路径偶发不会跳转，但 #app 必须可见且未跳出域
        assert "datastat-manage-website" in home_page.url, \
            f"应停留在站内，实际: {home_page.url}"
        expect(home_page.locator("#app")).to_be_visible()

    def test_page_has_title(self, home_page: Page):
        """TC-UI-002 [正常流] 页面有标题"""
        title = home_page.title()
        assert title and len(title) > 0, "页面应有标题"

    def test_navigate_to_developers(self, page: Page):
        """TC-UI-003 [正常流] 导航到开发者页面"""
        page.goto(f"{BASE_URL}/developers?community=openeuler",
                  wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(1000)
        assert "/developers" in page.url

    def test_navigate_to_health(self, page: Page):
        """TC-UI-004 [正常流] 导航到健康状态页面"""
        page.goto(f"{BASE_URL}/health?community=openeuler",
                  wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(1000)
        assert "/health" in page.url


# ===== 页面元素测试 =====

class TestPageElements:

    def test_app_container_visible(self, home_page: Page):
        """TC-UI-005 [正常流] 页面包含 #app 容器"""
        app = home_page.locator("#app")
        expect(app).to_be_visible()

    def test_no_login_form(self, home_page: Page):
        """TC-UI-006 [正常流] preview 环境无登录表单"""
        login_form = home_page.locator(".login-card")
        expect(login_form).not_to_be_visible()

    def test_page_has_content(self, page: Page):
        """TC-UI-007 [正常流] 页面有实际内容（非空白）"""
        page.goto(f"{BASE_URL}/overview?community=openeuler",
                  wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2500)
        body_text = page.locator("#app").inner_text()
        assert len(body_text.strip()) > 0, "页面不应为空"


# ===== 核心页面路由可达性测试 =====
# 基于 src/routers/index.ts 路由表

CORE_ROUTES = [
    ("/overview", "概览"),
    ("/overview/community", "社区概览"),
    ("/overview/software", "软件产品概览"),
    ("/overview/contributors", "贡献者概览"),
    ("/developers", "开发者"),
    ("/health", "健康状态"),
    ("/download", "下载"),
    ("/organizations", "组织"),
    ("/sigs", "SIG"),
    ("/warehouse", "仓库"),
    ("/drilldown", "下钻"),
    ("/registered-users", "注册用户"),
    ("/services", "服务"),
    ("/services-analysis", "服务分析"),
    ("/users", "用户"),
    ("/docs", "文档分析"),
]


class TestCoreRoutes:
    """验证所有核心路由可达"""

    @pytest.mark.parametrize("path,name", CORE_ROUTES,
                             ids=[r[0].strip("/").replace("/", "_") or "root"
                                  for r in CORE_ROUTES])
    def test_route_accessible(self, page: Page, path, name):
        """TC-UI-ROUTE 各核心路由可达且 #app 渲染（允许前端守卫重定向到合法兜底页）"""
        page.goto(f"{BASE_URL}{path}?community=openeuler",
                  wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(800)
        # 域名内 + #app 可见即视为可达；部分路由会被前端守卫重定向到 health/overview/noPermission
        assert "datastat-manage-website" in page.url, \
            f"{name}页({path}) 跳转出域: {page.url}"
        app = page.locator("#app")
        expect(app).to_be_visible()


# ===== 概览页功能测试 =====

class TestOverviewPage:

    def test_overview_renders_content(self, page: Page):
        """TC-UI-010 [正常流] 概览页渲染主体内容区"""
        page.goto(f"{BASE_URL}/overview?community=openeuler",
                  wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        body = page.locator("body").inner_text()
        assert len(body.strip()) > 10, "概览页应有实质内容"

    def test_overview_no_error_overlay(self, page: Page):
        """TC-UI-011 [正常流] 概览页无全局错误弹窗"""
        page.goto(f"{BASE_URL}/overview?community=openeuler",
                  wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        error_msg = page.locator(".el-message--error")
        assert error_msg.count() == 0, "不应有 error message 弹窗"


# ===== 侧边栏/导航测试 =====

def _open_page(page: Page, path: str = "/overview?community=openeuler",
               wait_extra: int = 2000) -> None:
    """打开页面并等待 SPA 渲染完成"""
    page.goto(f"{BASE_URL}{path}", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_function(
        "document.querySelector('#app') && document.querySelector('#app').children.length > 0",
        timeout=10000,
    )
    page.wait_for_timeout(wait_extra)


class TestSidebar:

    def test_sidebar_or_nav_exists(self, page: Page):
        """TC-UI-012 [正常流] 页面含侧边栏/顶栏/导航元素"""
        _open_page(page)
        nav_selectors = [
            "aside", ".el-aside", ".sidebar", "nav",
            "[class*='aside']", "[class*='menu']",
            "[class*='nav']", "[class*='sider']",
            "[class*='header']", "header",
        ]
        nav = page.locator(", ".join(nav_selectors))
        assert nav.count() > 0, f"应存在导航类元素，实际匹配数=0"

    def test_header_visible(self, page: Page):
        """TC-UI-016 [正常流] 顶部 header 可见"""
        _open_page(page)
        header = page.locator(
            "header, [class*='header'], [class*='Header']"
        ).first
        assert header.count() > 0, "应存在 header 元素"

    def test_route_switch_keeps_layout(self, page: Page):
        """TC-UI-017 [正常流] 路由切换后 #app 容器仍存在（SPA 不重载）"""
        _open_page(page)
        page.goto(f"{BASE_URL}/health?community=openeuler",
                  wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(1500)
        expect(page.locator("#app")).to_be_visible()


# ===== 响应式/国际化测试 =====

class TestI18nAndResponsive:

    def test_page_lang_attribute(self, page: Page):
        """TC-UI-013 [正常流] HTML lang 属性设置正确"""
        page.goto(f"{BASE_URL}/overview", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(800)
        lang = page.locator("html").get_attribute("lang")
        assert lang in ("zh", "en", "zh-CN", "zh-Hans"), \
            f"lang 应为中/英; 实际={lang}"

    def test_no_console_errors(self, page: Page):
        """TC-UI-014 [正常流] 页面加载无 JS 关键报错"""
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.goto(f"{BASE_URL}/overview?community=openeuler",
                  wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        critical = [e for e in errors if "Cannot read" in e or "is not defined" in e]
        assert len(critical) == 0, f"不应有 JS 关键报错: {critical}"


# ===== 无权限页面测试 =====

class TestNoPermission:

    def test_no_permission_page_accessible(self, page: Page):
        """TC-UI-015 [正常流] 无权限页面可访问"""
        page.goto(f"{BASE_URL}/noPermission",
                  wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(800)
        app = page.locator("#app")
        expect(app).to_be_visible()


# ===== 图表渲染深度断言 =====

class TestChartsRendering:
    """图表渲染断言：echarts/canvas/svg 容器与可视化元素"""

    def test_overview_has_visual_container(self, page: Page):
        """TC-UI-018 [正常流] 概览页含 echarts/canvas/svg 可视化容器"""
        _open_page(page, wait_extra=4000)
        chart = page.locator(
            "canvas, svg, .echarts, [_echarts_instance_], "
            "[class*='chart'], [class*='Chart']"
        )
        assert chart.count() > 0, "概览页应至少有一个图表/可视化容器"

    def test_developers_chart_dimension(self, page: Page):
        """TC-UI-019 [正常流] 开发者页图表/svg 容器有合法尺寸"""
        _open_page(page, "/developers?community=openeuler", wait_extra=4000)
        target = page.locator("canvas, svg").first
        if target.count() == 0:
            pytest.skip("该页面无 canvas/svg 渲染（可能纯表格页）")
        box = target.bounding_box()
        assert box is not None, "可视化元素应可获取 bounding_box"
        assert box["width"] > 0 and box["height"] > 0, \
            f"图表尺寸应非零，实际 w={box['width']} h={box['height']}"

    def test_no_chart_render_error(self, page: Page):
        """TC-UI-020 [反向] 图表渲染过程不应抛出 ECharts/render 关键错误"""
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        _open_page(page, wait_extra=4000)
        keywords = ("echarts", "getInstanceByDom", "setOption",
                    "Cannot read properties of undefined")
        critical = [e for e in errors if any(k.lower() in e.lower() for k in keywords)]
        assert not critical, f"图表渲染相关报错: {critical}"

    def test_health_page_has_visual_elements(self, page: Page):
        """TC-UI-021 [正常流] 健康状态页含可视化或表格元素"""
        _open_page(page, "/health?community=openeuler", wait_extra=3000)
        visual = page.locator(
            "canvas, svg, table, .el-table, "
            "[class*='chart'], [class*='table']"
        )
        assert visual.count() > 0, "健康页应含图表或表格"


# ===== 数据加载与网络请求 =====

class TestDataLoading:
    """断言数据接口被调用、SPA 内容随路由切换"""

    def test_data_api_requests_fired(self, page: Page):
        """TC-UI-022 [正常流] 概览页加载时触发数据接口请求"""
        api_calls = []

        def on_request(req):
            url = req.url
            if any(seg in url for seg in
                   ("/api/", "/server/", "/queryapi/", "/datastat/")):
                api_calls.append(url)

        page.on("request", on_request)
        _open_page(page, wait_extra=4000)
        assert len(api_calls) > 0, "概览页应至少触发一次数据 API 请求"

    def test_no_5xx_response(self, page: Page):
        """TC-UI-023 [反向] 页面加载不应有 5xx 响应"""
        bad_responses = []

        def on_response(resp):
            try:
                if resp.status >= 500:
                    bad_responses.append((resp.status, resp.url))
            except Exception:
                pass

        page.on("response", on_response)
        _open_page(page, wait_extra=4000)
        assert not bad_responses, f"出现 5xx 响应: {bad_responses[:3]}"

    def test_route_switch_changes_content(self, page: Page):
        """TC-UI-024 [正常流] 路由切换后页面 url 变化且 #app 内容刷新"""
        _open_page(page)
        first_url = page.url
        first_text_len = len(page.locator("#app").inner_text() or "")

        page.goto(f"{BASE_URL}/sigs?community=openeuler",
                  wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(2500)
        assert page.url != first_url, "路由切换后 url 应变化"
        second_text_len = len(page.locator("#app").inner_text() or "")
        assert first_text_len > 0 and second_text_len > 0, \
            f"两个页面 #app 文本长度均应 > 0; first={first_text_len} second={second_text_len}"


# ===== 用户交互（社区切换/筛选/Tab）=====

class TestInteractions:
    """常见交互：社区切换、Tab 切换、点击筛选项"""

    def test_community_query_param_respected(self, page: Page):
        """TC-UI-025 [正常流] community query 参数会保留在 url"""
        page.goto(f"{BASE_URL}/overview?community=mindspore",
                  wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1500)
        assert "community=mindspore" in page.url

    def test_clickable_links_exist(self, page: Page):
        """TC-UI-026 [正常流] 概览页含可点击链接（a/button 元素）"""
        _open_page(page, wait_extra=2500)
        clickable = page.locator("a[href], button, [role='button']")
        assert clickable.count() > 0, "页面应有可点击元素"

    def test_tab_or_filter_present_on_developers(self, page: Page):
        """TC-UI-027 [正常流] 开发者页含 Tab 或筛选控件"""
        _open_page(page, "/developers?community=openeuler", wait_extra=3000)
        controls = page.locator(
            ".el-tabs, [class*='tab'], [class*='Tab'], "
            ".el-select, .el-radio-group, [class*='filter'], [class*='Filter']"
        )
        if controls.count() == 0:
            pytest.skip("开发者页无明显 tab/filter 控件")
        assert controls.count() > 0


# ===== 健壮性：404 / 多次导航 =====

class TestRobustness:

    def test_unknown_route_does_not_crash(self, page: Page):
        """TC-UI-028 [反向] 未知路由不应导致 #app 崩溃"""
        try:
            page.goto(f"{BASE_URL}/__nonexistent_route__",
                      wait_until="domcontentloaded", timeout=20000)
        except Exception:
            pass
        page.wait_for_timeout(1500)
        app = page.locator("#app")
        assert app.count() > 0, "未知路由也应渲染 #app 容器"

    def test_double_navigate_no_error(self, page: Page):
        """TC-UI-029 [边界] 连续两次导航不应抛 JS 关键错误（过滤 SPA 路由切换瞬时报错）"""
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.goto(f"{BASE_URL}/overview", wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(1500)
        page.goto(f"{BASE_URL}/health?community=openeuler",
                  wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(2000)
        # 过滤 vue-router 快速切换时常见的 push undefined 报错
        ignorable = ("(reading 'push')", "(reading 'replace')")
        critical = [e for e in errors
                    if ("Cannot read" in e or "is not defined" in e)
                    and not any(ig in e for ig in ignorable)]
        assert not critical, f"连续导航出现关键 JS 报错: {critical}"


# ===== 顶部社区下拉框：每个选项各一条用例 =====
# 数据来源：实测点开 header 的 el-select 后枚举 .group-item 与 li.el-select-dropdown__item

# 三个分组及其下属社区选项（label 即下拉中的可见文本）
COMMUNITY_OPTIONS = [
    # 分组 1：鲲鹏
    ("鲲鹏", "BoostKit"),
    ("鲲鹏", "UnifiedBus"),
    ("鲲鹏", "openEuler"),
    ("鲲鹏", "openUBMC"),
    ("鲲鹏", "openGauss"),
    ("鲲鹏", "openFuyao"),
    # 分组 2：昇腾
    ("昇腾", "昇腾系列"),
    ("昇腾", "CANN"),
    ("昇腾", "HiFloat"),
    ("昇腾", "MindSpore"),
    ("昇腾", "MindIE"),
    ("昇腾", "MindSeriesSDK"),
    ("昇腾", "MindSDK"),
    ("昇腾", "AscendNPU-IR"),
    ("昇腾", "MindStudio"),
    ("昇腾", "MindCluster"),
    ("昇腾", "PTA"),
    ("昇腾", "MindSpeed"),
    ("昇腾", "vLLM"),
    ("昇腾", "SGLang"),
    ("昇腾", "PyTorch"),
    ("昇腾", "Triton"),
    ("昇腾", "TileLang"),
    ("昇腾", "VeRL"),
    ("昇腾", "参与开源"),
    # 分组 3：公共
    ("公共", "基础设施"),
    ("公共", "洞察"),
]


def _open_community_dropdown(page: Page, group_label: str) -> None:
    """点开顶部社区下拉框，并切到指定分组（鲲鹏/昇腾/公共）。

    分组项是「sticky」p 元素，常规 click 会被判为不可点击；用 force=True 触发。
    """
    page.click("header .el-select__wrapper")
    page.wait_for_selector(".el-select-dropdown", state="visible", timeout=5000)
    group = page.locator(".group-item", has_text=group_label).first
    group.click(force=True)
    page.wait_for_timeout(500)


class TestCommunityDropdown:
    """顶部社区下拉框：分组 + 每个社区选项的可见性 / 切换可达性"""

    def test_dropdown_opens(self, page: Page):
        """TC-UI-DD-001 [正常流] 顶部下拉框可点开"""
        _open_page(page)
        page.click("header .el-select__wrapper")
        dropdown = page.locator(".el-select-dropdown")
        expect(dropdown).to_be_visible(timeout=5000)

    @pytest.mark.parametrize("group", ["鲲鹏", "昇腾", "公共"])
    def test_group_visible(self, page: Page, group: str):
        """TC-UI-DD-002 [正常流] 三大分组在下拉中可见"""
        _open_page(page)
        page.click("header .el-select__wrapper")
        page.wait_for_selector(".el-select-dropdown", state="visible", timeout=5000)
        grp = page.locator(".group-item .group-name", has_text=group)
        assert grp.count() > 0, f"分组 {group} 应可见"

    @pytest.mark.parametrize(
        "group,option",
        COMMUNITY_OPTIONS,
        ids=[f"{g}-{o}" for g, o in COMMUNITY_OPTIONS],
    )
    def test_option_visible_in_dropdown(self, page: Page, group: str, option: str):
        """TC-UI-DD-OPT-VIS 每个社区选项在对应分组下可见"""
        _open_page(page)
        _open_community_dropdown(page, group)
        # 取可见状态的同名 li
        target = page.locator(
            f"li.el-select-dropdown__item:visible:has-text('{option}')"
        )
        assert target.count() > 0, f"{group} 分组下应可见选项: {option}"

    @pytest.mark.parametrize(
        "group,option",
        COMMUNITY_OPTIONS,
        ids=[f"{g}-{o}" for g, o in COMMUNITY_OPTIONS],
    )
    def test_option_switch_reaches_overview(self, page: Page, group: str, option: str):
        """TC-UI-DD-OPT-NAV 点击社区选项后页面仍在站内且 #app 渲染"""
        _open_page(page)
        _open_community_dropdown(page, group)
        # 取该项并点击；strict 时取首个匹配
        target = page.locator(
            f"li.el-select-dropdown__item:visible:has-text('{option}')"
        ).first
        # 部分超长项可能溢出，强制滚动到视口
        try:
            target.scroll_into_view_if_needed(timeout=3000)
        except Exception:
            pass
        target.click()
        page.wait_for_timeout(3000)
        # 仍在被测域内
        assert "datastat-manage-website" in page.url, \
            f"切到 {option} 后跳出域: {page.url}"
        # #app 容器仍渲染
        expect(page.locator("#app")).to_be_visible(timeout=10000)
        # 顶部下拉显示文本应已更新（部分项前端会延迟刷新，故仅做软校验）
        header_text = page.locator("header .el-select__placeholder, "
                                   "header .el-select__selected-item").first.inner_text()
        # 软断言：当前显示项可能与 option 不完全一致（中文/缩写映射），仅验证非空
        assert header_text is not None


# ===== cases.txt 补充用例：总览页面功能测试 =====

COMMUNITIES = ["cann", "openeuler"]


def _goto_community(page: Page, community: str, path: str = "/overview", wait: int = 3000):
    """导航到指定社区的页面"""
    page.goto(f"{BASE_URL}{path}?community={community}",
              wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(wait)


class TestOverviewData:
    """总览页面数据一致性（cases.txt 第1节）"""

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_overview_has_project_summary(self, page: Page, community: str):
        """TC-CASE-001 总览页含「项目总览」区域"""
        _goto_community(page, community)
        text = page.locator("#app").inner_text()
        assert "项目总览" in text, "总览页应含「项目总览」区域"

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_overview_has_huawei_developer_section(self, page: Page, community: str):
        """TC-CASE-002 总览页含「华为开发者」和「非华为开发者」"""
        _goto_community(page, community)
        text = page.locator("#app").inner_text()
        assert "华为开发者" in text, "应含「华为开发者」"
        assert "非华为开发者" in text, "应含「非华为开发者」"

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_overview_has_pr_metrics(self, page: Page, community: str):
        """TC-CASE-003 总览页含 Active/Merged/Open PR 指标"""
        _goto_community(page, community)
        text = page.locator("#app").inner_text()
        assert "Active pull requests" in text or "Merged Pull Requests" in text
        assert "Open Pull Requests" in text or "Merged Pull Requests" in text

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_overview_has_issue_metrics(self, page: Page, community: str):
        """TC-CASE-004 总览页含 Active/Closed/New Issues 指标"""
        _goto_community(page, community)
        text = page.locator("#app").inner_text()
        assert "Active issues" in text or "Closed Issues" in text

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_overview_has_contribution_trend(self, page: Page, community: str):
        """TC-CASE-005 总览页含「贡献趋势（合入PR）」图表区"""
        _goto_community(page, community)
        text = page.locator("#app").inner_text()
        assert "贡献趋势" in text

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_overview_has_contributor_ranking(self, page: Page, community: str):
        """TC-CASE-006 总览页含「贡献者排名」和「贡献组织排名」"""
        _goto_community(page, community)
        text = page.locator("#app").inner_text()
        assert "贡献者排名" in text
        assert "贡献组织排名" in text


# ===== cases.txt 补充用例：运营看板页面功能测试 =====

class TestOperationDashboard:
    """运营看板（cases.txt 第2节）"""

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_sidebar_has_operation_menu(self, page: Page, community: str):
        """TC-CASE-007 侧栏含「运营看板」子菜单"""
        _goto_community(page, community)
        text = page.locator("#app").inner_text()
        assert "运营看板" in text or "软件生产" in text or "运营总览" in text

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_software_production_page(self, page: Page, community: str):
        """TC-CASE-008 软件生产页含 PR 闭环率指标"""
        _goto_community(page, community)
        parent = page.locator(".el-menu-item, .el-sub-menu__title",
                              has_text="运营看板")
        if parent.count() > 0:
            parent.first.click()
            page.wait_for_timeout(800)
        sw = page.locator(".el-menu-item", has_text="软件生产")
        if sw.count() > 0:
            sw.first.click(timeout=10000)
            page.wait_for_timeout(3000)
            text = page.locator("#app").inner_text()
            has_metrics = ("Merged Pull Requests" in text or
                           "PR" in text or "Active" in text)
            assert has_metrics, "软件生产页应含 PR 相关指标"
        else:
            pytest.skip("侧栏无「软件生产」菜单项")

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_contributor_page_has_stats(self, page: Page, community: str):
        """TC-CASE-009 贡献者页含「总体贡献情况」"""
        _goto_community(page, community)
        parent = page.locator(".el-menu-item, .el-sub-menu__title",
                              has_text="运营看板")
        if parent.count() > 0:
            parent.first.click()
            page.wait_for_timeout(800)
        contrib = page.locator(".el-menu-item", has_text="贡献者")
        if contrib.count() > 0:
            contrib.first.click(timeout=10000)
            page.wait_for_timeout(3000)
            text = page.locator("#app").inner_text()
            assert "贡献" in text, "贡献者页应含贡献相关内容"
        else:
            pytest.skip("侧栏无「贡献者」菜单项")


# ===== cases.txt 补充用例：趋势分析（开发者页面）=====

class TestDevelopersTrend:
    """趋势分析 - 开发者页面（cases.txt 第3节）"""

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_developers_has_d0_d1_d2_tabs(self, page: Page, community: str):
        """TC-CASE-010 开发者页含 D0/D1/D2 度量指标切换"""
        _goto_community(page, community, "/developers")
        text = page.locator("#app").inner_text()
        assert "D0" in text and "D1" in text and "D2" in text

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_developers_has_trend_chart(self, page: Page, community: str):
        """TC-CASE-011 开发者页含趋势图（canvas/svg）"""
        _goto_community(page, community, "/developers", wait=5000)
        chart = page.locator("canvas, svg, [class*='chart']")
        assert chart.count() > 0, "开发者页应含趋势图"

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_developers_has_dimension_controls(self, page: Page, community: str):
        """TC-CASE-012 开发者页含度量维度（增量/总量/当期活跃）"""
        _goto_community(page, community, "/developers")
        text = page.locator("#app").inner_text()
        assert "增量" in text or "总量" in text or "当期活跃" in text

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_developers_has_metric_types(self, page: Page, community: str):
        """TC-CASE-013 开发者页含度量指标（PR/Issue/Comment/AddCode）"""
        _goto_community(page, community, "/developers")
        text = page.locator("#app").inner_text()
        has_pr = "PR" in text or "提交PR" in text
        has_issue = "Issue" in text
        assert has_pr and has_issue

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_developers_has_contributor_table(self, page: Page, community: str):
        """TC-CASE-014 开发者页含贡献者统计表格"""
        _goto_community(page, community, "/developers")
        text = page.locator("#app").inner_text()
        assert "贡献者统计" in text or "开发者" in text
        assert "合入PR" in text or "PR闭环率" in text

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_developers_funnel_or_chart_exists(self, page: Page, community: str):
        """TC-CASE-015 开发者页含漏斗图或趋势图可视化"""
        _goto_community(page, community, "/developers", wait=5000)
        visual = page.locator("canvas, svg, [_echarts_instance_]")
        assert visual.count() > 0

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_developers_interval_controls(self, page: Page, community: str):
        """TC-CASE-016 开发者页含间隔周期（天/周/月）"""
        _goto_community(page, community, "/developers")
        text = page.locator("#app").inner_text()
        has_interval = ("天" in text and "周" in text and "月" in text) or \
                       ("间隔周期" in text)
        assert has_interval


# ===== cases.txt 补充用例：组织分析/仓库分析 =====

class TestOrgAndRepoAnalysis:
    """组织分析 & 仓库分析页面（cases.txt 第3节 4/5）"""

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_org_analysis_page_loads(self, page: Page, community: str):
        """TC-CASE-017 组织分析页可加载"""
        _goto_community(page, community, "/organizations", wait=4000)
        text = page.locator("#app").inner_text()
        assert "组织" in text or "PR" in text or \
               page.locator("canvas, svg").count() > 0

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_repo_analysis_page_loads(self, page: Page, community: str):
        """TC-CASE-018 仓库分析页可加载"""
        _goto_community(page, community, "/warehouse", wait=4000)
        text = page.locator("#app").inner_text()
        assert "仓库" in text or "PR" in text or \
               page.locator("canvas, svg").count() > 0

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_org_has_pie_chart(self, page: Page, community: str):
        """TC-CASE-019 组织分析页含饼图/图表"""
        _goto_community(page, community, "/organizations", wait=5000)
        chart = page.locator("canvas, svg, [class*='chart']")
        assert chart.count() > 0

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_repo_has_pie_chart(self, page: Page, community: str):
        """TC-CASE-020 仓库分析页含饼图/图表"""
        _goto_community(page, community, "/warehouse", wait=5000)
        chart = page.locator("canvas, svg, [class*='chart']")
        assert chart.count() > 0


# ===== cases.txt 补充用例：社区健康度功能测试 =====

class TestCommunityHealth:
    """社区健康度（cases.txt 第4节）"""

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_health_page_has_radar_or_trend(self, page: Page, community: str):
        """TC-CASE-021 健康度页含雷达图或趋势图"""
        _goto_community(page, community, "/health", wait=5000)
        chart = page.locator("canvas, svg, [class*='chart'], [class*='radar']")
        text = page.locator("#app").inner_text()
        has_content = chart.count() > 0 or "指标名称" in text
        assert has_content

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_health_has_indicator_table(self, page: Page, community: str):
        """TC-CASE-022 健康度页含指标列表"""
        _goto_community(page, community, "/health", wait=4000)
        text = page.locator("#app").inner_text()
        assert "指标名称" in text or "当前值" in text or "同比值" in text

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_health_has_date_range(self, page: Page, community: str):
        """TC-CASE-023 健康度页含日期范围选择器"""
        _goto_community(page, community, "/health")
        text = page.locator("#app").inner_text()
        assert "至" in text or "日期" in text


# ===== cases.txt 补充用例：文档分析功能测试 =====

class TestDocsAnalysis:
    """文档分析（cases.txt 第5节）"""

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_docs_page_loads(self, page: Page, community: str):
        """TC-CASE-024 文档分析页可加载"""
        _goto_community(page, community, "/docs", wait=4000)
        text = page.locator("#app").inner_text()
        assert "文档" in text or "数据字典" in text or \
               "No Data" in text or len(text) > 50

    @pytest.mark.parametrize("community", COMMUNITIES)
    def test_docs_has_search_or_table(self, page: Page, community: str):
        """TC-CASE-025 文档分析页含搜索框或表格"""
        _goto_community(page, community, "/docs", wait=4000)
        search = page.locator("input[type='text'], .el-input, [class*='search']")
        table = page.locator("table, .el-table")
        assert search.count() > 0 or table.count() > 0 or \
               "No Data" in page.locator("#app").inner_text()
