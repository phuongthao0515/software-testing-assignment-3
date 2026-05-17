from asyncio import wait
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.data import DEFAULT


class NewForumPage:
    """Class NewForumPage contains methods to interact with the new forum page of the Moodle. 
    """
    
    def __init__(self, driver: webdriver.Chrome, wait: WebDriverWait):
        self.driver = driver
        self.wait = wait
        
    
    def expand_all(self):
        self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Expand all']"))
        ).click()
        
        
    def fill_TextField(self, locatorType: By, locator: str, value: str):
        # skip if value is DEFAULT (use existing value)
        if value == DEFAULT:
            return
        
        self.wait.until(EC.element_to_be_clickable((locatorType, locator))).send_keys(value)
        print("-- Forum Name filled")


    def fill_WholeForumGrading(self, row):
        if row["WFG_GradeType"] == DEFAULT:
            return
        
        #Scroll to grading section
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", 
            self.driver.find_element(By.ID, "collapseElement-6" )
        )
        time.sleep(0.5)  # Small pause to allow scroll to finish
        self.driver.find_element(By.ID, "collapseElement-6" ).click()
        time.sleep(0.5)  # Small pause to allow section to expand
        
        # WFG_GradeType        
        Select(self.wait.until(
                EC.element_to_be_clickable((By.ID, "id_grade_forum_modgrade_type"))
            )).select_by_visible_text(row["WFG_GradeType"])
        print("-- WFG_GradeType filled")
        
        # WFG_MaxGrade (only if WFG_GradeType is Point)
        if row["WFG_GradeType"] == "Point":
            max_grade_field = self.wait.until(
                EC.element_to_be_clickable((By.ID, "id_grade_forum_modgrade_point"))
            )
            max_grade_field.clear()
            max_grade_field.send_keys(row["WFG_MaxGrade"])
            print("-- WFG_MaxGrade filled")

        # WFG_GradeToPass
        grade_to_pass_field = self.wait.until(
            EC.element_to_be_clickable((By.ID, "id_gradepass_forum"))
            )
        grade_to_pass_field.clear()  # Clear existing value before entering new one
        grade_to_pass_field.send_keys(row["WFG_GradeToPass"])
        print("-- WFG_GradeToPass filled")
        
        print("-- Whole Forum Grading filled")


    def fill_Ratings(self, row):
        if row["R_AggType"] == DEFAULT:
            return
        
        # Scroll to ratings section
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", 
            self.wait.until(EC.element_to_be_clickable((By.ID, "collapseElement-7")))
        )
        time.sleep(0.5)  # Small pause to allow scroll to finish
        self.wait.until(EC.element_to_be_clickable((By.ID, "collapseElement-7"))).click()
        time.sleep(0.5)  # Small pause to allow section to expand
        
        # R_AggType
        Select(
            self.wait.until(EC.element_to_be_clickable((By.ID, "id_assessed")))
            ).select_by_visible_text(row["R_AggType"])
        print("-- R_AggType filled")
        
        # R_ScaleType
        field = self.wait.until(EC.element_to_be_clickable((By.ID, "id_scale_modgrade_type")))
        field.click()
        time.sleep(0.5)  # Small pause to allow dropdown to open
        Select(field).select_by_visible_text(row["R_ScaleType"])
        print("-- R_ScaleType filled")
        
        # R_MaxGrade (only if R_ScaleType is Point)
        if row["R_ScaleType"] == "Point":
            max_grade_field = self.wait.until(EC.element_to_be_clickable((By.ID, "id_scale_modgrade_point")))
            max_grade_field.clear()
            max_grade_field.send_keys(row["R_MaxGrade"])
            print("-- R_MaxGrade filled")
        
        # R_GradeToPass
        if row["R_GradeToPass"] != DEFAULT:
            grade_to_pass_field = self.wait.until(EC.element_to_be_clickable((By.ID, "id_gradepass")))
            grade_to_pass_field.clear()
            grade_to_pass_field.send_keys(row["R_GradeToPass"])
            print("-- R_GradeToPass filled")
        
        print("-- Ratings filled")

    
    def fill_Availability(self, row):
        if row["A_DDate_Year"] == DEFAULT and row["A_CDate_Year"] == DEFAULT:
            return
        
        # Scroll to availability section
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", 
            self.wait.until(EC.element_to_be_clickable((By.ID, "collapseElement-1")))
        )
        time.sleep(0.5)  # Small pause to allow scroll to finish
        
        # expand section
        self.wait.until(EC.element_to_be_clickable((By.ID, "collapseElement-1"))).click()
        time.sleep(0.5)  # Small pause to allow section to expand
       
        if row["A_DDate_Year"] != DEFAULT:
           self.wait.until(EC.element_to_be_clickable((By.ID, "id_duedate_enabled"))).click()
           print("-- Due Date enabled")
           
        if row["A_CDate_Year"] != DEFAULT:
            self.wait.until(EC.element_to_be_clickable((By.ID, "id_cutoffdate_enabled"))).click()
            print("-- Cut-off Date enabled")
            
            if row["A_CDate_Year"] != "ENABLED":
                Select(
                    self.wait.until(EC.element_to_be_clickable((By.ID, "id_cutoffdate_year")))
                ).select_by_visible_text(row["A_CDate_Year"])   
        
        print("-- Availability filled")
       
    
    def fill_ForumDescription(self, description, should_show=True):
        if description == DEFAULT:
            return
        
        # Forum description is inside a tinymce iframe, need to switch to it before filling
        iframe = self.driver.find_element(By.CSS_SELECTOR, "iframe")
        self.driver.switch_to.frame(iframe)
        
        editor = self.driver.find_element(By.ID, "tinymce")
        editor.clear()
        editor.send_keys(description)
        
        # Switch back to main content after filling description
        self.driver.switch_to.default_content()
        print("-- Forum Description filled")
        
        # Show description
        if should_show:
            # Scroll to show description checkbox
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                self.wait.until(EC.element_to_be_clickable((By.ID, "id_showdescription")))
            )
            time.sleep(0.5)  # Small pause to allow scroll to finish
            self.wait.until(EC.element_to_be_clickable((By.ID, "id_showdescription"))).click()
            print("-- Show description enabled")
            
    
    def fill_ForumType(self, forum_type):
        if forum_type == DEFAULT:
            return
        
        Select(
            self.wait.until(EC.element_to_be_clickable((By.ID, "id_type")))
        ).select_by_visible_text(forum_type)
        print("-- Forum Type filled")
        
        
    def fill_Attachments_WordCount(self, maxBytes, maxAttcm, displayWrdCnt):        
        # Scroll to attachments & word count section
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", 
            self.wait.until(EC.element_to_be_clickable((By.ID, "collapseElement-2")))
        )
        time.sleep(0.5)  # Small pause to allow scroll to finish
        self.wait.until(EC.element_to_be_clickable((By.ID, "collapseElement-2"))).click()
        time.sleep(0.5)  # Small pause to allow section to expand
        
        # MaxBytes
        Select(
            self.wait.until(EC.element_to_be_clickable((By.ID, "id_maxbytes")))
        ).select_by_visible_text(maxBytes)
        print("-- MaxBytes filled")
        
        # MaxAttcm
        Select(
            self.wait.until(EC.element_to_be_clickable((By.ID, "id_maxattachments")))
        ).select_by_visible_text(maxAttcm)
        print("-- Attachments filled")
        
        # DisplayWrdCnt
        Select(
            self.wait.until(EC.element_to_be_clickable((By.ID, "id_displaywordcount")))
        ).select_by_visible_text(displayWrdCnt)
        print("-- Word count filled")


    def fill_Subscription_Tracking(self, forceSub, readTracking):        
        # Scroll to subscription section
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", 
            self.wait.until(EC.element_to_be_clickable((By.ID, "collapseElement-3")))
        )
        time.sleep(0.5)  # Small pause to allow scroll to finish
        self.wait.until(EC.element_to_be_clickable((By.ID, "collapseElement-3"))).click()
        time.sleep(0.5)  # Small pause to allow section to expand
        
        # ForceSub
        Select(
            self.wait.until(EC.element_to_be_clickable((By.ID, "id_forcesubscribe")))
        ).select_by_visible_text(forceSub)
        print("-- Subscription filled")
        
        # ReadTracking
        Select(
            self.wait.until(EC.element_to_be_clickable((By.ID, "id_trackingtype")))
        ).select_by_visible_text(readTracking)
        print("-- Read tracking filled")


    def fill_DiscussionLocking(self, lockDscEnbl, lockDscNum, lockDscTime):
        # Scroll to discussion locking section
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", 
            self.wait.until(EC.element_to_be_clickable((By.ID, "collapseElement-4")))
        )
        time.sleep(0.5)  # Small pause to allow scroll to finish
        self.wait.until(EC.element_to_be_clickable((By.ID, "collapseElement-4"))).click()
        time.sleep(0.5)  # Small pause to allow section to expand
        
        # LockDscEnbl
        if lockDscEnbl == "YES":
            self.wait.until(EC.element_to_be_clickable((By.ID, "id_lockdiscussionafter_enabled"))).click()
            print("-- Discussion locking enabled")
            
            # LockDscNum
            field = self.wait.until(EC.element_to_be_clickable((By.ID, "id_lockdiscussionafter_number")))
            field.clear()
            field.send_keys(lockDscNum)
            print("-- Lock discussion after number of posts filled")
            
            # LockDscTime
            Select(
            self.wait.until(EC.element_to_be_clickable((By.ID, "id_lockdiscussionafter_timeunit")))
            ).select_by_visible_text(lockDscTime)
            print("-- Lock discussion after time filled")


    def fill_PostThresholdBlocking(self, blockPeriod, blockAfter, warnAfter):
        # Scroll to post threshold blocking section
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            self.wait.until(EC.element_to_be_clickable((By.ID, "collapseElement-5")))
        )
        time.sleep(0.5)  # Small pause to allow scroll to finish  
        self.wait.until(EC.element_to_be_clickable((By.ID, "collapseElement-5"))).click()
        time.sleep(0.5)  # Small pause to allow section to expand
        
        # BlockPeriod
        Select(
            self.wait.until(EC.element_to_be_clickable((By.ID, "id_blockperiod")))
        ).select_by_visible_text(blockPeriod)
        print("-- Block period filled")
        
        # BlockAfter
        field = self.wait.until(EC.element_to_be_clickable((By.ID, "id_blockafter")))
        field.clear()
        field.send_keys(blockAfter)
        print("-- Block after filled")
        
        # WarnAfter
        field = self.wait.until(EC.element_to_be_clickable((By.ID, "id_warnafter")))
        field.clear()
        field.send_keys(warnAfter)
        print("-- Warn after filled")       
        
        
    def fill_CommonModuleSettings(self, visible, cmntNum, lang, groupMode): 
        # Scroll to common module settings section
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            self.wait.until(EC.element_to_be_clickable((By.ID, "collapseElement-8")))
        )
        time.sleep(0.5)  # Small pause to allow scroll to finish
        self.wait.until(EC.element_to_be_clickable((By.ID, "collapseElement-8"))).click()
        time.sleep(0.5)  # Small pause to allow section to expand
        
        # Visible
        Select(
            self.wait.until(EC.element_to_be_clickable((By.ID, "id_visible")))
        ).select_by_visible_text(visible)
        print("-- Visible filled")
        
        # CommentNum
        field = self.wait.until(EC.element_to_be_clickable((By.ID, "id_cmidnumber")))
        field.clear()
        field.send_keys(cmntNum)
        print("-- Comment number filled")
        
        # Language
        Select(
            self.wait.until(EC.element_to_be_clickable((By.ID, "id_lang")))
        ).select_by_visible_text(lang)
        print("-- Language filled")
        
        # GroupMode
        Select(
            self.wait.until(EC.element_to_be_clickable((By.ID, "id_groupmode")))
        ).select_by_visible_text(groupMode)
        print("-- Group mode filled")


    def fill_RestrictAccess(self, availCond, minGradePercent):
        # Scroll to restrict access section
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            self.wait.until(EC.element_to_be_clickable((By.ID, "collapseElement-9")))
        )
        time.sleep(0.5)  # Small pause to allow scroll to finish
        self.wait.until(EC.element_to_be_clickable((By.ID, "collapseElement-9"))).click()
        time.sleep(0.5)  # Small pause to allow section to expand
        
        # Click "Add restriction" button
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Add restriction...']"))).click()
        time.sleep(0.5)
        self.wait.until(EC.element_to_be_clickable((By.ID, "availability_addrestriction_grade"))).click()
        time.sleep(0.5)  # Small pause to allow restriction options to load
        
        Select(
            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='fitem_id_availabilityconditionsjson']//select[@name='id']")))
        ).select_by_visible_text(availCond)
        
        # Condtion value
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox' and @name='min']"))).click()  # Check "Minimum grade" checkbox to enable the input field
        
        field = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@title='Minimum grade percentage (inclusive)']")))
        field.clear()
        field.send_keys(minGradePercent)
        
        print("-- Restrict access filled")
        
        
    def fill_CompleteConditions(self, compCond):
        # Scroll to activity completion section
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            self.wait.until(EC.element_to_be_clickable((By.ID, "collapseElement-10")))
        )
        time.sleep(0.5)  # Small pause to allow scroll to finish
        self.wait.until(EC.element_to_be_clickable((By.ID, "collapseElement-10"))).click()
        time.sleep(0.5)  # Small pause to allow section to expand
        
        id = {
            "NONE": "id_completion_0",
            "MANUAL_MARK": "id_completion_1",
            "ADD_REQUIREMENT": "id_completion_2"
        }
        
        self.wait.until(EC.element_to_be_clickable((By.ID, id[compCond]))).click()
        print("-- Completion conditions enabled")
        
        
    def fill_Tags(self, tag):
        # Scroll to tags section
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            self.wait.until(EC.element_to_be_clickable((By.ID, "collapseElement-11")))
        )
        time.sleep(0.5)  # Small pause to allow scroll to finish
        self.wait.until(EC.element_to_be_clickable((By.ID, "collapseElement-11"))).click()
        time.sleep(0.5)  # Small pause to allow section to expand
        
        field = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Enter tags...']")))
        field.clear()
        field.send_keys(tag)
        print("-- Tags filled")
        
        
    def fill_Competency(self, competency):
        # Scroll to competency section
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            self.wait.until(EC.element_to_be_clickable((By.ID, "collapseElement-12")))
        )
        time.sleep(0.5)  # Small pause to allow scroll to finish
        self.wait.until(EC.element_to_be_clickable((By.ID, "collapseElement-12"))).click()
        time.sleep(0.5)  # Small pause to allow section to expand 
        
        Select(
            self.wait.until(EC.element_to_be_clickable((By.ID, "id_competency_rule")))
        ).select_by_visible_text(competency)
        
        print("-- Competency filled")
        
        
    def fill_SendNoti(self, sendNoti):        
        if sendNoti == "YES":
            # Scroll to send notifications section
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                self.wait.until(EC.element_to_be_clickable((By.ID, "id_coursecontentnotification")))
            )
            self.wait.until(EC.element_to_be_clickable((By.ID, "id_coursecontentnotification"))).click()
            print("-- Send notifications enabled")


    def get_CreatedForumName(self):
        # Wait for page Forum to load and header to be visible
        # self.wait.until(
        #     EC.visibility_of_element_located(
        #         (By.XPATH, "//header[@id='page-header']//h1[contains(text(),'Forum')]")
        #     )
        # )  
            
        forum_name = self.wait.until(EC.presence_of_element_located((By.XPATH, "//h1[@class='h2 mb-0']"))).text
        return forum_name
        
    
    def get_ForumNameError(self):
        err_message = self.wait.until(EC.presence_of_element_located((By.ID, "id_error_name"))).text
        return err_message
    
    
    def get_WFG_GradeToPassError(self):
        err_message = self.wait.until(EC.presence_of_element_located((By.ID, "id_error_gradepass_forum"))).text
        return err_message


    def get_R_GradeToPassError(self):
        err_message = self.wait.until(EC.presence_of_element_located((By.ID, "id_error_gradepass"))).text
        return err_message
    
    
    def get_WFG_ForumGradeValueError(self):
        err_message = self.wait.until(EC.presence_of_element_located((By.ID, "fgroup_id_error_grade_forum"))).text
        return err_message
    
    
    def get_R_GradeValueError(self):
        err_message = self.wait.until(EC.presence_of_element_located((By.ID, "fgroup_id_error_scale"))).text
        return err_message


    def get_WFG_GradeValueError(self):
        err_message = self.wait.until(EC.presence_of_element_located((By.ID, "id_error_grade_forum"))).text
        return err_message


    def get_AvailabilityError(self):
        err_message = self.wait.until(EC.presence_of_element_located((By.ID, "id_error_cutoffdate"))).text
        return err_message


    def get_AggTypeError(self):
        err_message = self.wait.until(EC.presence_of_element_located((By.ID, "id_error_assessed"))).text
        return err_message


    def open_create_forum_page(self):
        self.driver.get("https://sandbox.moodledemo.net/course/view.php?id=2")
        time.sleep(0.5) 

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", 
            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[2]/div[2]/div/div/button/i")))
        )
        time.sleep(2)  # Small pause to allow scroll to finish
        self.driver.find_element(By.XPATH, "//div[2]/div[2]/div/div/button/i").click()
        print("--Plus button clicked")

        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[2]/div[2]/div/div/div/button/i"))).click()
        time.sleep(1)  # Small pause to allow popup to open
        self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Forum"))).click()
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-action='add-selected-chooser-option']"))).click()
        time.sleep(2)   

        print(self.driver.current_url)
        print("CREATE FORUM PAGE OPENED")


    def submit_form(self):
        self.wait.until(EC.element_to_be_clickable((By.ID, "id_submitbutton"))).click()
        print("-- Form submitted")
        time.sleep(2)  # Small pause to allow form submission to process
        
    
    def click_cancel(self):
        self.wait.until(EC.element_to_be_clickable((By.ID, "id_cancel"))).click()
        print("-- Cancel button clicked")
        time.sleep(1.5)  # Small pause to allow cancellation to process
        
    
    def click_return_to_course_btn(self):
        self.wait.until(EC.element_to_be_clickable((By.ID, "id_submitbutton2"))).click()
        print("-- Return to course link clicked")
        time.sleep(1.5)  # Small pause to allow page to load
