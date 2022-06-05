from dotenv import load_dotenv
import os
import dj_database_url

def get_db_config(base_dir):
    # load_dotenv()
    # if os.getenv('ENVIRONMENT') == "production":
    #     return {
    #         'default': dj_database_url.config()
    #     }
    # else:
    #     return {
    #         'default': {
    #             'ENGINE': 'django.db.backends.sqlite3',
    #             'NAME': base_dir / 'db.sqlite3',
    #         }
    #     }
    return {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': base_dir / 'db.sqlite3',
            }
        }