import re
from flask import flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Email, ValidationError
from app import cursor, cursor_dict


class RegisterForm(FlaskForm):
    
    firstname = StringField('ชื่อจริง', validators=[DataRequired(message="กรุณากรอกชื่อจริง"),
                                                Length(min=2, max=45, message="ชื่อจริงต้องมีความยาว 2-45 ตัวอักษร")]) 
    lastname = StringField('นามสกุล', validators=[DataRequired(message="กรุณากรอกนามสกุล"),
                                                Length(min=2, max=45, message="นามสกุลต้องมีความยาว 2-45 ตัวอักษร")] )
    email = StringField('E-mail', validators=[DataRequired(message="กรุณากรอกEmail"),
                                             Email(message="รูปแบบ E-mail ไม่ถูกต้อง")])
    username = StringField('ชื่อผู้ใช้', validators=[DataRequired(message="กรุณากรอกชื่อผู้ใช้"),
                                                Length(min=6, max=20, message="ชื่อผู้ใช้ต้องมีความยาว 6-20 ตัวอักษร")])
    password = PasswordField('รหัสผ่าน', validators=[DataRequired(message="กรุณากรอกรหัสผ่าน"),
                                                    Length(min=4, max=16, message="รหัสผ่านต้องมีความยาว 4-16 ตัวอักษร")])
    confirm_password = PasswordField('ยืนยันรหัสผ่าน', validators=[EqualTo('password',message="รหัสผ่านยืนยันไม่ถูกต้อง"),
                                                            DataRequired(message="กรุณากรอกรหัสผ่านยืนยัน")])
    submit = SubmitField('สมัครสมาชิก')

    def validate_user(self):
        # check username
        cursor.execute(f"SELECT username FROM user WHERE username = {self.username.data}")
        data = cursor_dict.fetchone()
        if data:
            raise ValidationError(f'มีชื่อผู้ใช้ {data[0]} อยู่ในระบบแล้ว')
        
        # check email
        cursor.execute(f"SELECT email FROM user WHERE email = {self.email.data}")
        data = cursor_dict.fetchone()
        if data:
            raise ValidationError(f'มี E-mail {data[0]} อยู่ในระบบแล้ว')
        


class LoginForm(FlaskForm):

    username = StringField('ชื่อผู้ใช้', validators=[DataRequired(message="กรุณากรอกชื่อผู้ใช้")])
    password = PasswordField('รหัสผ่าน', validators=[DataRequired(message="กรุณากรอกรหัสผ่าน")])
    submit = SubmitField('เข้าสู่ระบบ')

    def validate_user(self):
        # check username
        cursor.execute(f"SELECT username FROM user WHERE username = {self.username.data}")
        data = cursor.fetchone()
        if data is None:
            raise ValidationError("ไม่มีชื่อผู้ใช้นี้ในระบบ")
        
        # check email
        cursor.execute(f"SELECT password FROM user WHERE username = {self.username.data}")
        data = cursor.fetchone()
        if data != self.password.data:
            raise ValidationError("รหัสผ่านไม่ถูกต้อง")

            



    


   











