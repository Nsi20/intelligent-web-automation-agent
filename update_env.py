import os

env_path = '.env'
target_email = 'nsidibedaniel62@gmail.com'

def update_env():
    if not os.path.exists(env_path):
        print(f"{env_path} not found!")
        return

    with open(env_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    email_to_found = False
    email_enabled_found = False

    for line in lines:
        if line.startswith('EMAIL_TO='):
            new_lines.append(f'EMAIL_TO={target_email}\n')
            email_to_found = True
        elif line.startswith('EMAIL_ENABLED='):
            new_lines.append('EMAIL_ENABLED=true\n')
            email_enabled_found = True
        else:
            new_lines.append(line)

    if not email_to_found:
        new_lines.append(f'\nEMAIL_TO={target_email}\n')
    
    if not email_enabled_found:
        new_lines.append('EMAIL_ENABLED=true\n')

    with open(env_path, 'w') as f:
        f.writelines(new_lines)
    
    print(f"Updated {env_path} with EMAIL_TO={target_email}")

if __name__ == "__main__":
    update_env()
