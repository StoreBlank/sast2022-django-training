from .models import Submission, User
from random import randint
import functools

def get_leaderboard():
    """
    Get the current leaderboard
    :return: list[dict]
    """

    # 坏了，我似乎已经忘了 ORM 中该怎么调 API 了
    # 在这里你可选择
    #    1. 看一眼数据表, 然后后裸写 SQL
    #    2. 把所有数据一股脑取回来然后手工选出每个用户的最后一次提交
    #    3. 学习 Django API 完成这个查询

    # 方案1: 直接裸写 SQL 摆烂，注意，由于数据库类型等因素，这个查询未必能正确执行，如果使用这种方法可能需要进行调整
    # subs = list(Submission.objects.raw(
    #         """
    #         SELECT
    #             `lb_submission`.`id`,
    #             `lb_submission`.`avatar`,
    #             `lb_submission`.`score`,
    #             `lb_submission`.`subs`,
    #             `lb_submission`.`time`
    #         FROM `lb_submission`, (
    #             SELECT `user_id`, MAX(`time`) AS mt FROM `lb_submission` GROUP BY `user_id`
    #         ) `sq`
    #         WHERE
    #             `lb_submission`.`user_id`=`sq`.`user_id` AND
    #             `time`=`sq`.`mt`;
    #         ORDER BY
    #             `lb_submission`.`subs` DESC,
    #             `lb_submission`.`time` ASC
    #         ;
    #         """
    # ))
    # return [
    #     {
    #         "user": obj.user.username,
    #         "score": obj.score,
    #         "subs": [int(x) for x in obj.subs.split()],
    #         "avatar": obj.avatar,
    #         "time": obj.time,
    #         "votes": obj.user.votes
    #     }
    #     for obj in subs
    # ]

    # 方案2：一股脑拿回本地计算
    all_submission = Submission.objects.all()
    subs = {}
    for s in all_submission:
        if s.user_id not in subs or (s.user_id in subs and s.time > subs[s.user_id].time):
            subs[s.user_id] = s

    subs = sorted(subs.values(), key=lambda x: (-x.score, x.time))
    return [
        {
            "user": obj.user.username,
            "score": obj.score,
            "subs": [int(x) for x in obj.subs.split()],
            "avatar": obj.avatar,
            "time": obj.time,
            "votes": obj.user.votes
        }
        for obj in subs
    ]

    # 方案3：调用 Django 的 API (俺不会了
    # ...

def judge(content: str):
    """
    Convert submitted content to a main score and a list of sub scors
    :param content: the submitted content to be judged
    :return: main score, list[sub score]
    """

    # TODO: Use `ground_truth.txt` and the content to calculate scores.
    #  If `content` is invalid, raise an Exception so that it can be
    #  captured in the view function.
    #  You can define the calculation of main score arbitrarily.
    subs = [0, 0, 0]

    with open("lb/ground_truth.txt") as f:
        truth = f.read().strip().split("\n")[1:]
    
    truth_0 = [eval(line.split(",")[1]) for line in truth]
    truth_1 = [eval(line.split(",")[2]) for line in truth]
    truth_2 = [eval(line.split(",")[3]) for line in truth]

    content_lines = content.strip().split("\n")
    if len(content_lines) != len(truth_0):
        raise AssertionError("The number of lines is wrong")
    subs[0] = sum([(truth_0[i] == eval(content_lines[i].split(",")[0])) for i in range(len(truth_0))]) / len(truth_0)
    subs[1] = sum([(truth_1[i] == eval(content_lines[i].split(",")[1])) for i in range(len(truth_0))]) / len(truth_0)
    subs[2] = sum([(truth_2[i] == eval(content_lines[i].split(",")[2])) for i in range(len(truth_0))]) / len(truth_0)

    return 114514, subs

def get_history(username: str):
    all_submission = Submission.objects.all()
    submissions = [s for s in all_submission if s.user.username == username]

    if len(submissions) == 0:
        return {
            "code": -1
        }

    return [
        {
            "score": s.score,
            "subs": s.subs,
            "time": s.time
        } for s in submissions
    ]