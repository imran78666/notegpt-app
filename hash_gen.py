import streamlit_authenticator as stauth

passwords = ['1234', '5678', 'abcd']
hashed_passwords = stauth.Hasher().generate(passwords)

print(hashed_passwords)
