from datetime import datetime, timezone

#note for devs: this should always be set to a couple minutes in the future when pushing
#there is a pre-commit hook that will do this for you, ask Guy if you don't have it!
VERSION_DATE = datetime(2023, 8, 31, 17, 54, 2, tzinfo=timezone.utc)