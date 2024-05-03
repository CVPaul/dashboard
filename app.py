#!/usr/bin/env python
#-*- coding:utf-8 -*-


import os
import glob
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Trader-XII", layout='wide')


def line2dic(line):
    res = {}
    toks = line.split(',')
    for tk in toks:
        kv = tk.split('=')
        res[kv[0].strip()] = kv[1].strip()
    return res


def log_parser(filename):
    content = []
    with open(filename) as fp:
        for line in fp:
            if "/WIN" in line or "/LOSS" in line:
                direct = 'LONG' if 'LONG' in line else 'SHORT'
                action = 'OPEN' if 'OPEN' in line else 'CLOSE'
                line = f'direct={direct},action={action},' + line.split("|")[1]
                content.append(line2dic(line))
    df = pd.DataFrame(content)
    if df.empty:
        return "## No Trade History Now!", {"### All Trade History":df}
    df['open'] = df.enpp
    if 'price' in df.columns:
        df['close'] = df.price.fillna(df.spp)
    else:
        df['close'] = df.spp
    df.open = df.open.astype(float)
    df.close = df.close.astype(float)
    df['side'] = df.direct.apply(lambda x: 1 if x == 'LONG' else -1)
    df['gross'] = df.side * (df.close - df.open)
    df['commis'] = (df.close + df.open) * 0.0005
    df.index = pd.to_datetime(df.pop('st').astype(float) * 1e6)
    res = {}
    #if df.shape[0] > 60:
    #    res["### Head-30"] = df.head(30)
    #    res["### Tail-30"] = df.tail(30)
    #else:
    #    res["### All Trade History"] = df
    res["### All Trade History"] = df
    trade_days = (df.index[-1] - df.index[0]).days
    summary = f'''## Trade Summary
    - start-time: {df.index[0]}
    - stop-time: {df.index[-1]}
    - trade-days: {trade_days}
    - trade-cnt: {df.shape[0]}
    - trade-cnt/day: {df.shape[0] / trade_days if trade_days else 0}
    - gross: {df.gross.sum():.6f}
    - commis: {df.commis.sum():.6f}
    - net-value: {(df.gross - df.commis).sum():.6f}'''
    return summary, res


def main():
    default = "请选择..."
    cols = st.columns([1, 1])
    with cols[0]:
        symbol = st.selectbox(
            "币种：", options=[default, "BTC", "BNB", "DOGE"])
    with cols[1]:
        if symbol == default:
            symbol = "*"
        else:
            symbol = symbol.lower()
        filename = st.selectbox(
            '日志文件：', options=[default] + sorted(
                glob.glob(f"./{symbol}-*.log")))
    if filename != default:
        summary, res = log_parser(filename)
        st.markdown(summary)
        for title, table in res.items():
            st.markdown(title)
            st.table(table)
    

if __name__ == "__main__":
    main()