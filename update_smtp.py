import os

env_path = '.env'
smtp_user = 'nsidibedaniel62@gmail.com'
smtp_password = 'wvfw ekyk qkvr xsug'

def update_env():
    if not os.path.exists(env_path):
        print(f"{env_path} not found!")
        return

    with open(env_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    user_found = False
    pass_found = False

    for line in lines:
        if line.startswith('SMTP_USER='):
            new_lines.append(f'SMTP_USER={smtp_user}\n')
            user_found = True
        elif line.startswith('SMTP_PASSWORD='):
            new_lines.append(f'SMTP_PASSWORD={smtp_password}\n')
            pass_found = True
        elif line.startswith('EMAIL_FROM='):
             new_lines.append(f'EMAIL_FROM={smtp_user}\n')
        else:
            new_lines.append(line)

    if not user_found:
        new_lines.append(f'\nSMTP_USER={smtp_user}\n')
    
    if not pass_found:
        new_lines.append(f'SMTP_PASSWORD={smtp_password}\n')

    with open(env_path, 'w') as f:
        f.writelines(new_lines)
    
    print(f"Updated {env_path} with SMTP credentials for {smtp_user}")

if __name__ == "__main__":
    update_env()
