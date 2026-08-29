"""Complete numeric members suggested by newly recovered BO4 attachment families."""
import sys

DBAL = "attach_t8_lmg_hades_dbal_{n}_{tail}"
BARREL = "attach_t8_sniper_vanguard_barrel_{n}_sig_{sig}_{tail}"


def main():
    count = 0
    for n in range(1, 17):
        for tail in ("view", "world"):
            print(DBAL.format(n=n, tail=tail))
            count += 1
            for sig in range(1, 17):
                print(BARREL.format(n=n, sig=f"{sig:02d}", tail=tail))
                count += 1
    print(f"{count:,} streamed attachment family completions", file=sys.stderr)


if __name__ == "__main__":
    main()
