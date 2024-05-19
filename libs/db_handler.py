import sqlite3
from os import getenv
from os.path import abspath, exists
from libs.crontask import Task
from libs.logger import logger

logger = logger(__name__)

db_path=abspath(getenv(
    'PYSS_SQLITE_DB_PATH',
    'schedule.db'
))

class Dbhandler():
    db_conn=None
    tasks_list=[]
    curr_task=None

    schedules_table = \
    """ CREATE TABLE IF NOT EXISTS tasks (
        id integer PRIMARY KEY,
        name text NOT NULL,
        minute text NOT NULL,
        hour text NOT NULL,
        dom text NOT NULL,
        mon text NOT NULL,
        dow text NOT NULL,
        command text NOT NULL
        ); """
    
    def __init__(self, db_file=db_path):
        self.db_file=db_file
        self.open()

    def open(self):
        db_exists=True
        try:
            if not exists (self.db_file):
                logger.msg(level='info', text='DB file not exists and will be created now')
                db_exists=False

            self.db_conn = sqlite3.connect(self.db_file)
            logger.msg(level='info', text='Connection to db opened')
            logger.msg(level='info', text=f"DB version: {sqlite3.version}")

            if not db_exists:
                self.schema_init()
        except sqlite3.Error as e:
            logger.msg(level='error', text='Cannot open db connection')
            logger.msg(level='error', text=e)
    
    def schema_init(self):
        logger.msg(level='info', text='Creating default db schema')
        
        try:
            c = self.db_conn.cursor()
            c.execute(self.schedules_table)
            logger.msg(level='info', text='Default DB schema created')
        except sqlite3.Error as e:
            logger.msg(level='error', text='Cannot create default db schema')
            logger.msg(level='error', text=e)

    def search_task(self, task):
        dow = "(dow LIKE '%" + "%' OR dow LIKE '%".join(task[5].split(',')) + "%')"
        sql = \
        """ SELECT * FROM tasks
            WHERE minute = '{}'
            AND hour = '{}'
            AND dom = '{}'
            AND mon = '{}'
            AND {}; """\
                .format(task[1],task[2],task[3],task[4],dow)
        
        try:
            c = self.db_conn.cursor()
            c.execute(sql)

            rows = c.fetchall()

            if len(rows) > 0:
                self.curr_task = Task(rows[0])
            else:
                self.curr_task=None
            logger.msg(level='info', text='Task search completed')
            logger.msg(level='debug', text=f"Tasks found: {str(self.curr_task)}")
        except sqlite3.Error as e:
            logger.msg(level='error', text='Cannot execute query')
            logger.msg(level='error', text=e)
            print(e)

    def insert_task(self, task):
        sql = \
        """ INSERT INTO tasks (name, minute, hour, dom, mon, dow, command)
            VALUES (?,?,?,?,?,?,?); """

        try:
            c = self.db_conn.cursor()
            c.execute(sql, task)
            self.db_conn.commit()
            logger.msg(level='info', text='New task created')
            logger.msg(level='debug', text=task)
        except sqlite3.Error as e:
            logger.msg(level='error', text='Cannot execute insert statement')
            logger.msg(level='error', text=e)
        
        return c.lastrowid
    
    def update_task(self, task):
        sql = \
        """ UPDATE tasks SET
            name = '{}',
            minute = '{}',
            hour = '{}',
            dom = '{}',
            mon = '{}',
            dow = '{}',
            command = '{}'
            WHERE id = {} """.format(
                task.getName(),
                task.getMinute(),
                task.getHour(),
                task.getDom(),
                task.getMon(),
                task.getDow(),
                task.getCommand(),
                task.getTid())

        try:
            c = self.db_conn.cursor()
            c.execute(sql)
            self.db_conn.commit()
            logger.msg(level='info', text='Task updated')
            logger.msg(level='debug', text=task)
        except sqlite3.Error as e:
            logger.msg(level='info', text='Cannot execute update statement')
            logger.msg(level='info', text=e)
        
        return c.lastrowid

    def list_tasks(self):
        sql = "SELECT * FROM tasks ORDER BY hour + 0 ASC, minute + 0 ASC, dow ASC;"

        c = self.db_conn.cursor()
        c.execute(sql)

        rows = c.fetchall()

        for row in rows:
            self.curr_task = Task(row)
            self.tasks_list.append(self.curr_task)

    def delete_task(self, task_id):
        sql = " DELETE FROM tasks WHERE id = ?;"

        try:
            c = self.db_conn.cursor()
            c.execute(sql, (task_id,))
            self.db_conn.commit()
            logger.msg(level='info', text='Task deleted')
            logger.msg(level='debug', text=f"Deleted task id: {str(task_id)}")
        except sqlite3.Error as e:
            logger.msg(level='error', text='Cannot execute delete statement')
            logger.msg(level='error', text=e)

    def clear_all_tasks(self):
        try:
            c = self.db_conn.cursor()
            c.execute("DELETE FROM tasks;")
            self.db_conn.commit()
            c.execute("VACUUM;")
            self.db_conn.commit()
            logger.msg(level='info', text='Tasks table has been truncated')
        except sqlite3.Error as e:
            logger.msg(level='error', text='Cannot execute truncate query')
            logger.msg(level='error', text=e)

    def close(self):
        if self.db_conn:
            try:
                self.db_conn.close()
                logger.msg(level='info', text='Connection to db closed')
            except sqlite3.Error as e:
                logger.msg(level='error', text='Cannot close db connection')
                logger.msg(level='error', text=e)
