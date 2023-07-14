class FormatContent():
    '''Create list with format content
       The following methods form a common interface'''

    def create_req(self):
        pass

    def check_req(self):
        pass

    def delete_req(self):
        pass

    def create_content(self):
        pass

    def write_content(self, content):
        pass


class Latex(FormatContent):
    def __init__(self,latex_dir):
        self.dir = latex_dir
        self.template_file = "template.tex"
        self.joto_file = "joto.tex"
        self.content = []

    def create_req(self):
        os.makedirs(self.dir)

    def check_req(self):
        count = 2
        if os.path.exists(self.dir): count -= 1
        if os.path.exists(self.template_file): count -= 1
        if count == 0: return True
        else: return False

    def delete_req(self):
        if os.path.exists(self.dir): shutil.rmtree(self.dir)

    def create_content(self, db_data):
        shutil.copyfile(self.template_file,self.joto_file)
        date = None
        switch_star = False
        for row in db_data:
            prev_date = date
            date = row[1]
            text = row[2]
            image = row[3]

            # Empty line and switch column
            if prev_date != None:
                if not switch_star:
                    self.snpt_switch_empty_line()
                elif switch_star:
                    self.snpt_switch_star_empty_line()
                switch_star = not switch_star

            # Text only
            if image == "None":
                self.snpt_just_text(date,text)
            else:
                # Multiple images for same date
                if prev_date == date:
                    self.snpt_image_without_date(image,text)
                # Image with text - normal
                else:
                    self.snpt_image_with_text(date,image,text)

        self.snpt_switch_empty_line()
        self.snpt_end()

    def write_content(self):
        append_multiple_lines_to_file(self.joto_file, self.content)
        self.latexmk()

    def snpt_image_with_text(self,date,image,text):
        self.content.extend([
           self._add_date(date),
           self._add_empty_line(),
           self._add_image(image),
           self._add_empty_line(),
           self._add_text(text),
           self._add_empty_line()
        ])

    def snpt_image_without_date(self,image,text):
        self.content.extend([
           self._add_image(image),
           self._add_empty_line(),
           self._add_text(text),
           self._add_empty_line()
        ])

    def snpt_just_text(self,date,text):
        self.content.extend([
           self._add_date(date),
           self._add_empty_line(),
           self._add_text(text),
           self._add_empty_line()
        ])

    def snpt_switch_empty_line(self):
        self.content.extend([
           self._add_switch(),
           self._add_empty_line()
        ])

    def snpt_switch_star_empty_line(self):
        self.content.extend([
           self._add_switch_star(),
           self._add_empty_line()
        ])

    def snpt_end(self):
        '''Already a list'''
        self.content.extend(self._add_end())

    def _add_date(self,date):
        return "\section*{" + date + "}"

    def _add_image(self,image):
        '''Image size restricted by max size option'''
        # return "\includegraphics[height=\columnwidth,keepaspectratio]{" + image + "}"
        return "\includegraphics[max size={\columnwidth}{\columnwidth}]{" + image + "}"

    def _add_text(self,text):
        return text

    def _add_switch(self):
        return "\switchcolumn"

    def _add_switch_star(self):
        return "\switchcolumn*"

    def _add_empty_line(self):
        # pass
        return ""

    def _add_end(self):
        return ["\end{paracol}","\end{document}"]

    def latexmk(self):
        p = Popen(["latexmk", "-pdf", "-jobname=latex/joto", "joto.tex"], stdout=PIPE, stderr=PIPE)
        output, error = p.communicate()
        if p.returncode != 0:
            print("Latexmk failed  %d %s %s" % (p.returncode, output, error))