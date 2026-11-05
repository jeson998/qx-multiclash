#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一份源 -> 多端产物

输入  src/*.list           Clash / Surge 原生语法（DOMAIN-SUFFIX,xxx,PROXY）
输出  dist/qx/*.list       Quantumult X 语法（host-suffix, xxx, proxy）
      dist/clash/*.yaml    Clash rule-provider（behavior: classical）

用法: python scripts/build.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT_QX = ROOT / "dist" / "qx"
OUT_CLASH = ROOT / "dist" / "clash"

# Clash / Surge 类型 -> Quantumult X 类型
TYPE_MAP = {
    "DOMAIN-SUFFIX":  "host-suffix",
    "DOMAIN":         "host",
    "DOMAIN-KEYWORD": "host-keyword",
    "IP-CIDR":        "ip-cidr",
    "IP-CIDR6":       "ip6-cidr",
    "GEOIP":          "geoip",
    "MATCH":          "final",
}

POLICY_MAP = {"DIRECT": "direct", "PROXY": "proxy", "REJECT": "reject"}


def policy(name: str) -> str:
    return POLICY_MAP.get(name.strip().upper(), name.strip())


def to_qx(lines):
    out = []
    for raw in lines:
        s = raw.strip()
        if not s:
            continue
        if s.startswith("#"):
            out.append(s)
            continue

        p = [x.strip() for x in s.split(",")]
        t = p[0].upper()
        qt = TYPE_MAP.get(t)
        if qt is None:
            out.append(f"# [unsupported] {s}")
            continue

        if t == "MATCH":
            out.append(f"final, {policy(p[1])}")
            continue

        value = p[1].lower() if t == "GEOIP" else p[1]
        pol = policy(p[2]) if len(p) > 2 else "proxy"
        extra = ", no-resolve" if len(p) > 3 and p[3].lower() == "no-resolve" else ""
        out.append(f"{qt}, {value}, {pol}{extra}")
    return out


def to_clash_yaml(lines, tag):
    out = [
        f"# rule-provider: {tag}",
        "# 由 scripts/build.py 自动生成，请勿直接编辑",
        "payload:",
    ]
    for raw in lines:
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        if s.split(",")[0].upper() not in TYPE_MAP or s.split(",")[0].upper() == "MATCH":
            continue
        out.append(f"  - '{s}'")
    return out


def main():
    if not SRC.is_dir():
        sys.exit(f"src/ not found: {SRC}")

    OUT_QX.mkdir(parents=True, exist_ok=True)
    OUT_CLASH.mkdir(parents=True, exist_ok=True)

    total = 0
    for f in sorted(SRC.glob("*.list")):
        tag = f.stem
        lines = f.read_text(encoding="utf-8").splitlines()

        qx = to_qx(lines)
        (OUT_QX / f"{tag}.list").write_text("\n".join(qx) + "\n", encoding="utf-8")

        cy = to_clash_yaml(lines, tag)
        (OUT_CLASH / f"{tag}.yaml").write_text("\n".join(cy) + "\n", encoding="utf-8")

        n = sum(1 for l in qx if l.strip() and not l.startswith("#"))
        total += n
        print(f"  {tag:<10} {n:>4} rules  ->  dist/qx/{tag}.list | dist/clash/{tag}.yaml")

    print(f"\ndone: {total} rules converted")


if __name__ == "__main__":
    main()
