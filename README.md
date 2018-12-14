# imdb-reminder
A CLI tool for sending tv-show reminders via email.

## Installation

- Clone this directory \
`git clone https://github.com/parthsharma2/imdb-reminder.git`

- Enter the directory \
`cd imdb-reminder`

- Install the requirements \
`pip install -r requirements.txt`

- Open the `config.ini` and make changes as necessary
  - Replace `<enter_email_id>` with the email id you wish to use to send the emails from.
  - Replace `<password>` with your email password.
  - Replace `<host>` with the hostname of your email provider, eg: `smtp.gmail.com`
  - Replace `<port>` with the port number of the host, eg: `587`

## Usage
To run the script use the following command \
```
python3 imdb_reminder.py <EMAIL> <SHOWS>
```

Replace `<EMAIL>` with the email id to send the reminder. Replace `<SHOWS>` with a list of comma seperated show names.

## Example
```
python3 imdb_reminder.py abc@xyz friends, the big bang theory, brooklyn nine nine
```
Result: \
![Email Reminder](https://i.imgur.com/qD0Tfpu.png)
