def clamp(n, min_value, max_value):
    return max(min(n, max_value), min_value)

def heal(target,myself,amount):
    myself.now_hp = clamp(myself.now_hp + amount,0,myself.hp)

def damageTarget(target,myself,amount):
    target.now_hp = clamp(target.now_hp - amount,0,target.hp)


def useSkill(name,target,myself,amount):
    func = globals().get(name)
    if func:
        return func(target,myself,amount)
    else:
        return f"{name}은 존재하지 않는 능력입니다."
