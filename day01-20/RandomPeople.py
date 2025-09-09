import random

# 人员和工种
people = [
    ("姜海涛", "后端"),
    ("房方元", "后端"),
    ("孔得胜", "后端"),
    ("孙柏铃", "测试"),
    ("李星霖", "前端"),
    ("赵云鹏", "前端"),
    ("许亚西", "后端"),
    ("吴骁俊", "运维"),
]

def group_people(people):
    random.shuffle(people)  # 打乱顺序
    groups = []
    used = set()

    # 尝试优先匹配不同工种
    while len(used) < len(people):
        for i in range(len(people)):
            if i in used:
                continue
            p1, job1 = people[i]

            # 找到第一个工种不一样的
            partner_idx = None
            for j in range(i+1, len(people)):
                if j in used:
                    continue
                if people[j][1] != job1:  # 工种不同
                    partner_idx = j
                    break
            # 如果没找到不同工种的，就随便找一个
            if partner_idx is None:
                for j in range(i+1, len(people)):
                    if j not in used:
                        partner_idx = j
                        break

            p2, job2 = people[partner_idx]
            groups.append(((p1, job1), (p2, job2)))
            used.add(i)
            used.add(partner_idx)
            break

    return groups

if __name__ == "__main__":
    groups = group_people(people)
    print("分组结果：")
    for g in groups:
        print(f"{g[0][0]}({g[0][1]}) - {g[1][0]}({g[1][1]})")
