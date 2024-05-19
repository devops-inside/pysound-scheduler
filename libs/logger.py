import logging, os, subprocess

class logger():
    def __init__(self, app):
        self.log_path=os.path.abspath(os.getenv(
            'PYSS_LOG_PATH',
            'scheduler.log'
        ))

        self.levels = {
            'critical': logging.CRITICAL,
            'error': logging.ERROR,
            'warn': logging.WARNING,
            'warning': logging.WARNING,
            'info': logging.INFO,
            'debug': logging.DEBUG
        }

        self.log_level = self.levels.get(os.getenv(
            'PYSS_LOG_LEVEL',
            'info').lower()
        )

        log_dir = os.path.dirname(self.log_path)
        if not os.path.exists(log_dir):
            user = os.environ['USER']
            shell_out = subprocess.Popen(
                ["sudo", "mkdir", "-p", log_dir],
                stdout = subprocess.PIPE,
                stderr = subprocess.STDOUT)
            stdout,stderr = shell_out.communicate()
            if(stderr):
                print(stderr)
            shell_out = subprocess.Popen(
                ["sudo", "chown", "-R", user+":root", log_dir],
                stdout = subprocess.PIPE,
                stderr = subprocess.STDOUT)
            stdout,stderr = shell_out.communicate()
            if(stderr):
                print(stderr)
    
        self.logger = logging.getLogger(app)

        logging.basicConfig(
            format='%(asctime)s [%(levelname)-8s] %(name)s: %(message)s',
            filename=self.log_path,
            level=self.log_level,
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        self.logger.debug("Logs file initialized")

    def msg(self, level='info', text=None):
        if not text is None:
            level = self.levels.get(level)
            self.logger.log(level, msg=text)
