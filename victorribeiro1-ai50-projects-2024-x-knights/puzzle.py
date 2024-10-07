from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A claims to be both a knight and a knave.
knowledge0 = And(
    Not(And(AKnight, AKnave)),  # A cannot be both a knight and a knave
    Or(AKnight, AKnave),        # A is either a knight or a knave
    Implication(AKnight, And(AKnight, AKnave)),
    Implication(AKnave, Not(And(AKnight, AKnave)))
)

# Puzzle 1
# A says both A and B are knaves. B stays silent.
knowledge1 = And(
    Not(And(AKnight, AKnave)),  # A cannot be both a knight and a knave
    Or(AKnight, AKnave),        # A is either a knight or a knave

    Not(And(BKnight, BKnave)),  # B cannot be both a knight and a knave
    Or(BKnight, BKnave),        # B is either a knight or a knave

    Implication(AKnight, And(AKnave, BKnave)),
    Implication(AKnave, Not(And(AKnave, BKnave)))
)

# Puzzle 2
# A says A and B are the same type.
# B says A and B are different types.
knowledge2 = And(
    Not(And(AKnight, AKnave)),  # A cannot be both a knight and a knave
    Or(AKnight, AKnave),        # A is either a knight or a knave

    Not(And(BKnight, BKnave)),  # B cannot be both a knight and a knave
    Or(BKnight, BKnave),        # B is either a knight or a knave

    Implication(AKnight, And(AKnight, BKnight)),
    Implication(AKnave, Not(And(AKnave, BKnave))),

    Implication(BKnight, And(BKnight, AKnave)),
    Implication(BKnave, Not(And(BKnave, AKnight)))
)

# Puzzle 3
# A says "I am either a knight or a knave."
# B says A said, "I am a knave," and also claims that C is a knave.
# C says that A is a knight.
knowledge3 = And(
    Not(And(AKnight, AKnave)),  # A cannot be both a knight and a knave
    Or(AKnight, AKnave),        # A is either a knight or a knave

    Not(And(BKnight, BKnave)),  # B cannot be both a knight and a knave
    Or(BKnight, BKnave),        # B is either a knight or a knave

    Not(And(CKnight, CKnave)),  # C cannot be both a knight and a knave
    Or(CKnight, CKnave),        # C is either a knight or a knave

    # A says either "I am a knight." or "I am a knave."
    Or(
        And(Implication(AKnight, AKnight), Implication(AKnave, Not(AKnight))),
        And(Implication(AKnight, AKnave), Implication(AKnave, Not(AKnave)))
    ),

    Not(And(
        And(Implication(AKnight, AKnight), Implication(AKnave, Not(AKnight))),
        And(Implication(AKnight, AKnave), Implication(AKnave, Not(AKnave)))
    )),

    # B claims A said "I am a knave."
    Implication(BKnight, And(Implication(AKnight, AKnave), Implication(AKnave, Not(AKnave)))),

    Implication(BKnave, Not(And(Implication(AKnight, AKnave), Implication(AKnave, Not(AKnave))))),

    # B claims C is a knave.
    Implication(BKnight, CKnave),
    Implication(BKnave, Not(CKnave)),

    # C says A is a knight.
    Implication(CKnight, AKnight),
    Implication(CKnave, Not(AKnight))
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()