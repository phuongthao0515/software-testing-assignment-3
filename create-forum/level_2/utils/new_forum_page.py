import time

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from utils.data import DEFAULT
from utils.element_reader import ElementReader


class NewForumPage:
    """Interactions for Moodle's new forum page."""

    def __init__(self, driver: webdriver.Chrome, wait: WebDriverWait, config, elements: ElementReader):
        self.driver = driver
        self.wait = wait
        self.config = config
        self.elements = elements

    def locator(self, element_name):
        return self.elements.get(element_name)

    def wait_clickable(self, element_name):
        return self.wait.until(EC.element_to_be_clickable(self.locator(element_name)))

    def wait_present(self, element_name):
        return self.wait.until(EC.presence_of_element_located(self.locator(element_name)))

    def wait_visible(self, element_name):
        return self.wait.until(EC.visibility_of_element_located(self.locator(element_name)))

    def click(self, element_name):
        self.wait_clickable(element_name).click()

    def select_by_text(self, element_name, value):
        if value == DEFAULT:
            return

        Select(self.wait_clickable(element_name)).select_by_visible_text(value)

    def clear_and_type(self, element_name, value):
        if value == DEFAULT:
            return

        field = self.wait_clickable(element_name)
        field.clear()
        field.send_keys(value)

    def scroll_to(self, element_name):
        element = self.wait_clickable(element_name)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            element
        )
        time.sleep(0.5)
        return element

    def open_section(self, element_name):
        section = self.scroll_to(element_name)
        section.click()
        time.sleep(0.5)


    def fill_TextField(self, element_name: str, value: str):
        self.clear_and_type(element_name, value)
        print("-- Text field filled")

    def fill_WholeForumGrading(self, row):
        if row["WFG_GradeType"] == DEFAULT:
            return

        self.open_section("whole_forum_grading_section")

        self.select_by_text("whole_forum_grade_type_select", row["WFG_GradeType"])
        print("-- WFG_GradeType filled")

        if row["WFG_GradeType"] == "Point":
            self.clear_and_type("whole_forum_max_grade_field", row["WFG_MaxGrade"])
            print("-- WFG_MaxGrade filled")

        self.clear_and_type("whole_forum_grade_to_pass_field", row["WFG_GradeToPass"])
        print("-- WFG_GradeToPass filled")
        print("-- Whole Forum Grading filled")

    def fill_Ratings(self, row):
        if row["R_AggType"] == DEFAULT:
            return

        self.open_section("ratings_section")

        self.select_by_text("ratings_aggregate_type_select", row["R_AggType"])
        print("-- R_AggType filled")

        field = self.wait_clickable("ratings_scale_type_select")
        field.click()
        time.sleep(0.5)
        Select(field).select_by_visible_text(row["R_ScaleType"])
        print("-- R_ScaleType filled")

        if row["R_ScaleType"] == "Point":
            self.clear_and_type("ratings_max_grade_field", row["R_MaxGrade"])
            print("-- R_MaxGrade filled")

        if row["R_GradeToPass"] != DEFAULT:
            self.clear_and_type("ratings_grade_to_pass_field", row["R_GradeToPass"])
            print("-- R_GradeToPass filled")

        print("-- Ratings filled")

    def fill_Availability(self, row):
        if row["A_DDate_Year"] == DEFAULT and row["A_CDate_Year"] == DEFAULT:
            return

        self.open_section("availability_section")

        if row["A_DDate_Year"] != DEFAULT:
            self.click("due_date_enable_checkbox")
            print("-- Due Date enabled")

        if row["A_CDate_Year"] != DEFAULT:
            self.click("cutoff_date_enable_checkbox")
            print("-- Cut-off Date enabled")

            if row["A_CDate_Year"] != "ENABLED":
                self.select_by_text("cutoff_date_year_select", row["A_CDate_Year"])

        print("-- Availability filled")

    def fill_ForumDescription(self, description, should_show=True):
        if description == DEFAULT:
            return

        iframe = self.driver.find_element(*self.locator("forum_description_iframe"))
        self.driver.switch_to.frame(iframe)

        editor = self.driver.find_element(*self.locator("forum_description_editor"))
        editor.clear()
        editor.send_keys(description)

        self.driver.switch_to.default_content()
        print("-- Forum Description filled")

        if should_show:
            self.scroll_to("show_description_checkbox")
            self.click("show_description_checkbox")
            print("-- Show description enabled")

    def fill_ForumType(self, forum_type):
        self.select_by_text("forum_type_select", forum_type)
        print("-- Forum Type filled")

    def fill_Attachments_WordCount(self, maxBytes, maxAttcm, displayWrdCnt):
        self.open_section("attachments_word_count_section")

        self.select_by_text("max_bytes_select", maxBytes)
        print("-- MaxBytes filled")

        self.select_by_text("max_attachments_select", maxAttcm)
        print("-- Attachments filled")

        self.select_by_text("display_word_count_select", displayWrdCnt)
        print("-- Word count filled")

    def fill_Subscription_Tracking(self, forceSub, readTracking):
        self.open_section("subscription_tracking_section")

        self.select_by_text("subscription_mode_select", forceSub)
        print("-- Subscription filled")

        self.select_by_text("read_tracking_select", readTracking)
        print("-- Read tracking filled")

    def fill_DiscussionLocking(self, lockDscEnbl, lockDscNum, lockDscTime):
        self.open_section("discussion_locking_section")

        if lockDscEnbl == "YES":
            self.click("lock_discussion_enable_checkbox")
            print("-- Discussion locking enabled")

            self.clear_and_type("lock_discussion_number_field", lockDscNum)
            print("-- Lock discussion after number of posts filled")

            self.select_by_text("lock_discussion_time_unit_select", lockDscTime)
            print("-- Lock discussion after time filled")

    def fill_PostThresholdBlocking(self, blockPeriod, blockAfter, warnAfter):
        self.open_section("post_threshold_blocking_section")

        self.select_by_text("block_period_select", blockPeriod)
        print("-- Block period filled")

        self.clear_and_type("block_after_field", blockAfter)
        print("-- Block after filled")

        self.clear_and_type("warn_after_field", warnAfter)
        print("-- Warn after filled")

    def fill_CommonModuleSettings(self, visible, cmntNum, lang, groupMode):
        self.open_section("common_module_settings_section")

        self.select_by_text("visible_select", visible)
        print("-- Visible filled")

        self.clear_and_type("course_module_id_field", cmntNum)
        print("-- Comment number filled")

        self.select_by_text("language_select", lang)
        print("-- Language filled")

        self.select_by_text("group_mode_select", groupMode)
        print("-- Group mode filled")

    def fill_RestrictAccess(self, availCond, minGradePercent):
        self.open_section("restrict_access_section")

        self.click("add_restriction_button")
        time.sleep(0.5)
        self.click("grade_restriction_option")
        time.sleep(0.5)

        self.select_by_text("availability_condition_select", availCond)
        self.click("minimum_grade_checkbox")
        self.clear_and_type("minimum_grade_percentage_field", minGradePercent)

        print("-- Restrict access filled")

    def fill_CompleteConditions(self, compCond):
        self.open_section("activity_completion_section")

        completion_elements = {
            "NONE": "completion_none_radio",
            "MANUAL_MARK": "completion_manual_mark_radio",
            "ADD_REQUIREMENT": "completion_add_requirement_radio",
        }

        self.click(completion_elements[compCond])
        print("-- Completion conditions enabled")

    def fill_Tags(self, tag):
        self.open_section("tags_section")
        self.clear_and_type("tags_field", tag)
        print("-- Tags filled")

    def fill_Competency(self, competency):
        self.open_section("competencies_section")
        self.select_by_text("competency_rule_select", competency)
        print("-- Competency filled")

    def fill_SendNoti(self, sendNoti):
        if sendNoti == "YES":
            self.scroll_to("send_notifications_checkbox")
            self.click("send_notifications_checkbox")
            print("-- Send notifications enabled")

    def get_CreatedForumName(self):
        return self.wait_present("created_forum_name").text

    def get_ForumNameError(self):
        return self.wait_present("forum_name_error").text

    def get_WFG_GradeToPassError(self):
        return self.wait_present("whole_forum_grade_to_pass_error").text

    def get_R_GradeToPassError(self):
        return self.wait_present("ratings_grade_to_pass_error").text

    def get_WFG_ForumGradeValueError(self):
        return self.wait_present("whole_forum_grade_value_error").text

    def get_R_GradeValueError(self):
        return self.wait_present("ratings_grade_value_error").text

    def get_WFG_GradeValueError(self):
        return self.wait_present("whole_forum_grade_field_error").text

    def get_AvailabilityError(self):
        return self.wait_present("availability_error").text

    def get_AggTypeError(self):
        return self.wait_present("ratings_aggregate_type_error").text

    def get_CourseName(self):
        return self.wait_present("course_page_title").text

    def get_ForumNameOnCoursePage(self):
        return self.wait_present("forum_name_on_course_page").text

    def open_create_forum_page(self):
        self.driver.get(self.config["course_url"])
        time.sleep(0.5)

        self.scroll_to("add_activity_button")
        self.click("add_activity_button")
        print("--Plus button clicked")

        self.click("activity_chooser_button")
        time.sleep(1)
        self.click("forum_activity_link")
        self.click("add_selected_activity_button")
        time.sleep(1)

        print(self.driver.current_url)
        print("CREATE FORUM PAGE OPENED")

    def submit_form(self):
        self.click("save_and_display_button")
        print("-- Form submitted")
        time.sleep(2)

    def click_cancel(self):
        self.click("cancel_button")
        print("-- Cancel button clicked")
        time.sleep(1.5)

    def click_return_to_course_btn(self):
        self.click("save_and_return_to_course_button")
        print("-- Return to course link clicked")
        time.sleep(1.5)
