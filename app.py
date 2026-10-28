# ======================================
# CONFIG + Library Imports
# ======================================
import streamlit as st
import pandas as pd
import numpy as np
import math
import folium
import re
import io
import requests
import datetime
import os
import json
import time
import base64
import unicodedata
import html as html_lib
import hashlib
import hmac
import gzip
import secrets as pysecrets
import threading
import contextlib
import urllib.parse
from urllib.parse import unquote, quote
from xml.sax.saxutils import escape as xml_escape
from sklearn.cluster import KMeans
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Routing & Extractor System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================================================
# STYLING
# ==========================================================================================
ACCENT_GRADIENT = "linear-gradient(135deg, #2563EB 0%, #0D9488 100%)"

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, .main, p, div, span, h1, h2, h3, h4, h5, h6, label, button, textarea, input {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }

    .block-container {padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1200px;}

    /* ---------- Loading animation ---------- */
    .rp-loader {
        display: flex; flex-direction: column; align-items: center; gap: 0.7rem;
        padding: 1.3rem 1.1rem; margin: 0.6rem 0; text-align: center;
        border-radius: 18px; border: 1px solid rgba(37,99,235,0.28);
        background: linear-gradient(135deg, rgba(37,99,235,0.09), rgba(13,148,136,0.12));
        box-shadow: 0 8px 24px rgba(37,99,235,0.10);
    }
    .rp-track {position: relative; width: min(440px, 90%); height: 48px; margin-top: 2px;}
    .rp-line {
        position: absolute; left: 10px; right: 10px; top: 30px; height: 4px; border-radius: 4px; overflow: hidden;
        background: linear-gradient(90deg, #2563EB, #0D9488); opacity: 0.5;
    }
    .rp-line::after {
        content: ""; position: absolute; inset: 0;
        background: repeating-linear-gradient(90deg, rgba(255,255,255,0.9) 0 7px, transparent 7px 15px);
        animation: rp-dash 0.9s linear infinite;
    }
    .rp-stop {
        position: absolute; top: 23px; width: 16px; height: 16px; margin-left: -8px; box-sizing: border-box;
        border-radius: 50%; background: #fff; border: 3px solid #2563EB; animation: rp-stop 2.6s ease-in-out infinite;
    }
    .rp-stop.s1 {left: 4%;  animation-delay: 0.1s;}
    .rp-stop.s2 {left: 36%; animation-delay: 1.0s;}
    .rp-stop.s3 {left: 68%; animation-delay: 1.45s;}
    .rp-stop.s4 {left: 96%; animation-delay: 2.3s;}
    .rp-rocket {
        position: absolute; top: 3px; left: 0; width: 28px; height: 28px;
        animation: rp-drive 2.6s cubic-bezier(0.45, 0, 0.55, 1) infinite;
    }
    .rp-rocket span {   /* emoji roket menghadap kanan-atas; diputar 45° supaya melaju ke kanan */
        position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
        font-size: 24px; line-height: 1; transform: rotate(45deg);
        filter: drop-shadow(0 2px 3px rgba(0,0,0,0.22)); animation: rp-bob 0.45s ease-in-out infinite alternate;
    }
    .rp-flame {   /* jejak api di belakang roket */
        position: absolute; right: 70%; top: 50%; width: 38px; height: 5px; margin-top: -2px; border-radius: 6px;
        background: linear-gradient(90deg, rgba(251,146,60,0), rgba(251,146,60,0.85) 65%, rgba(250,204,21,0.95));
        transform-origin: right center; animation: rp-flame 0.16s ease-in-out infinite alternate;
    }
    @keyframes rp-bob {to {transform: rotate(45deg) translate(1px, -1px);}}
    @keyframes rp-flame {from {transform: scaleX(0.7); opacity: 0.7;} to {transform: scaleX(1.1); opacity: 1;}}
    .rp-title {font-weight: 700; font-size: 1.02rem;}
    .rp-sub {opacity: 0.9; font-size: 0.9rem; margin-top: -0.35rem;}
    .rp-dots b {display: inline-block; opacity: 0.2; animation: rp-blink 1.2s infinite;}
    .rp-dots b:nth-child(2) {animation-delay: 0.2s;}
    .rp-dots b:nth-child(3) {animation-delay: 0.4s;}
    .rp-bar {position: relative; width: min(440px, 90%); height: 8px; border-radius: 99px; overflow: hidden; background: rgba(127,127,127,0.2);}
    .rp-bar i {
        display: block; height: 100%; border-radius: 99px; transition: width 0.35s ease;
        background: linear-gradient(90deg, #2563EB, #0D9488, #2563EB); background-size: 200% 100%;
        animation: rp-shimmer 1.6s linear infinite;
    }
    .rp-indet i {width: 40%; animation: rp-shimmer 1.6s linear infinite, rp-slide 1.5s ease-in-out infinite;}
    .rp-pct {font-size: 0.85rem; opacity: 0.9; font-variant-numeric: tabular-nums;}
    @keyframes rp-drive {0% {left: 0;} 100% {left: calc(100% - 28px);}}
    @keyframes rp-dash {to {background-position: 15px 0;}}
    @keyframes rp-stop {
        0%, 100% {background: #fff; border-color: #2563EB; box-shadow: 0 0 0 0 rgba(13,148,136,0);}
        6% {background: #0D9488; border-color: #0D9488; box-shadow: 0 0 0 7px rgba(13,148,136,0.22);}
        24% {background: #fff; border-color: #2563EB; box-shadow: 0 0 0 0 rgba(13,148,136,0);}
    }
    @keyframes rp-blink {0%, 80%, 100% {opacity: 0.2;} 40% {opacity: 1;}}
    @keyframes rp-shimmer {to {background-position: -200% 0;}}
    @keyframes rp-slide {0% {margin-left: -40%;} 100% {margin-left: 100%;}}
    @media (prefers-reduced-motion: reduce) {
        .rp-loader *, .rp-loader *::after, .dev-badge, .dev-badge *, .app-footer *, .app-footer *::before {animation: none !important;}
    }
    /* Fokus keyboard yang jelas + teks khusus pembaca layar */
    button:focus-visible, a:focus-visible, summary:focus-visible, [role="tab"]:focus-visible, input:focus-visible {
        outline: 3px solid #2563EB !important; outline-offset: 2px;
    }
    .sr-only {position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0; overflow: hidden;
        clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0;}

    /* ---------- Hero header (banner judul halaman) ---------- */
    .hero-header {
        position: relative; display: flex; align-items: center; justify-content: space-between; gap: 24px;
        overflow: hidden; margin-bottom: 18px; padding: 24px 30px; border-radius: 20px;
        border: 1px solid rgba(37,99,235,0.22);
        background:
            radial-gradient(120% 150% at 0% 0%, rgba(37,99,235,0.15) 0%, rgba(37,99,235,0) 58%),
            radial-gradient(90% 130% at 100% 100%, rgba(13,148,136,0.15) 0%, rgba(13,148,136,0) 55%),
            rgba(128,128,128,0.04);
    }
    .hero-header::before {
        content: ""; position: absolute; left: 0; top: 20%; bottom: 20%; width: 3px; border-radius: 0 3px 3px 0;
        background: linear-gradient(180deg, #2563EB, #0D9488);
    }
    .hero-text {min-width: 0; position: relative;}
    .hero-eyebrow {
        display: flex; align-items: center; gap: 10px; margin-bottom: 8px;
        font-size: 0.72rem; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase; opacity: 0.85;
    }
    .hero-eyebrow::before {content: ""; width: 22px; height: 2px; border-radius: 2px; background: linear-gradient(90deg, #2563EB, #0D9488);}
    .hero-header h1 {
        margin: 0 !important; padding: 0 !important; color: inherit !important;
        font-size: 1.75rem; font-weight: 800; line-height: 1.25; letter-spacing: -0.01em;
    }
    .hero-header h1 .grad {
        background: linear-gradient(90deg, #2563EB, #0D9488); -webkit-background-clip: text; background-clip: text;
        color: transparent !important; -webkit-text-fill-color: transparent;
    }
    .hero-header p {
        margin: 8px 0 0 0 !important; max-width: 620px; font-size: 0.92rem; line-height: 1.55;
        color: inherit !important; opacity: 0.85;
    }
    .hero-art {flex: none; width: 210px; height: 84px;}
    .hero-route {stroke-dasharray: 2 9; animation: heroDash 2.4s linear infinite;}
    @keyframes heroDash {to {stroke-dashoffset: -22;}}
    @media (max-width: 720px) {
        .hero-art {display: none;}
        .hero-header {padding: 18px 20px;}
        .hero-header h1 {font-size: 1.4rem;}
    }

    /* ---------- Metric cards ---------- */
    .metric-card {
        background: rgba(128,128,128,0.08);
        border: 1px solid rgba(128,128,128,0.18);
        border-top: 3px solid #2563EB;
        border-radius: 14px;
        padding: 16px 18px;
        height: 100%;
    }
    .metric-card .metric-icon {font-size: 1.4rem; line-height: 1;}
    .metric-card .metric-label {
        font-size: 0.8rem; opacity: 0.9; margin-top: 8px; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.03em;
    }
    .metric-card .metric-value {font-size: 1.5rem; font-weight: 800; margin-top: 2px;}

    /* ---------- Sidebar ---------- */
    .sidebar-brand {display: flex; align-items: center; gap: 10px;}
    .sidebar-brand .emoji {font-size: 1.9rem; line-height: 1;}
    .sidebar-brand .title {font-weight: 800; font-size: 1.08rem; line-height: 1.2;}
    .sidebar-brand .subtitle {font-size: 0.82rem; opacity: 0.9;}

    /* ---------- Lencana "Developed by": jalur rute mini, titik bergerak melewati tiga pemberhentian ---------- */
    .dev-badge {
        position: relative; display: block; width: 100%; max-width: 300px; box-sizing: border-box;
        padding: 11px 16px 12px 11px; margin: 0 0 14px 0; border-radius: 16px;
        background: rgba(128,128,128,0.07);
    }
    .dev-badge::before {   /* garis tepi gradien tipis */
        content: ""; position: absolute; inset: 0; border-radius: inherit; padding: 1.5px; opacity: 0.8;
        background: linear-gradient(135deg, #2563EB, #0D9488);
        -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
        -webkit-mask-composite: xor; mask-composite: exclude; pointer-events: none;
    }
    .dev-top {display: flex; align-items: center; gap: 11px;}
    .dev-avatar {
        flex: none; width: 34px; height: 34px; border-radius: 50%; display: grid; place-items: center;
        font-weight: 800; font-size: 1rem; color: #ffffff;
        background: linear-gradient(135deg, #2563EB 0%, #0D9488 100%);
        box-shadow: 0 3px 12px rgba(13,148,136,0.38);
    }
    .dev-text {display: flex; flex-direction: column; line-height: 1.2; min-width: 0;}
    .dev-label {font-size: 0.72rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; opacity: 0.9; white-space: nowrap;}
    .dev-name {
        font-size: 1.05rem; font-weight: 800; letter-spacing: 0.02em; white-space: nowrap; width: fit-content;
        background: linear-gradient(90deg, #2563EB, #0D9488); -webkit-background-clip: text; background-clip: text;
        color: transparent; -webkit-text-fill-color: transparent;
    }
    .dev-route {position: relative; display: block; height: 14px; margin: 11px 7px 0 7px;}
    .dev-route::before {   /* jalan putus-putus */
        content: ""; position: absolute; left: 0; right: 0; top: 6px; height: 2px; border-radius: 2px;
        background: repeating-linear-gradient(90deg, rgba(128,128,128,0.6) 0 5px, transparent 5px 10px);
    }
    .dev-route .n {   /* titik pemberhentian: menyala saat dilewati */
        position: absolute; top: 2px; width: 10px; height: 10px; margin-left: -5px; box-sizing: border-box;
        border-radius: 50%; background: #ffffff; border: 2px solid #2563EB; animation: devNode 4s ease-in-out infinite;
    }
    .dev-route .n1 {left: 0;}
    .dev-route .n2 {left: 50%; animation-delay: 1.75s;}
    .dev-route .n3 {left: 100%; animation-delay: 3.5s;}
    .dev-pulse {   /* titik yang berjalan menyusuri rute */
        position: absolute; top: 1px; left: 0; width: 12px; height: 12px; margin-left: -6px; border-radius: 50%;
        background: linear-gradient(135deg, #2563EB, #0D9488);
        box-shadow: 0 0 0 4px rgba(13,148,136,0.18), 0 0 12px rgba(13,148,136,0.65);
        animation: devTravel 4s cubic-bezier(0.45, 0, 0.55, 1) infinite;
    }
    @keyframes devTravel {0% {left: 0; opacity: 0;} 8% {opacity: 1;} 92% {opacity: 1;} 100% {left: 100%; opacity: 0;}}
    @keyframes devNode {
        0% {background: #0D9488; border-color: #0D9488; box-shadow: 0 0 0 0 rgba(13,148,136,0);}
        8% {box-shadow: 0 0 0 6px rgba(13,148,136,0.25);}
        22% {background: #0D9488; border-color: #0D9488; box-shadow: 0 0 0 0 rgba(13,148,136,0);}
        34%, 100% {background: #ffffff; border-color: #2563EB; box-shadow: none;}
    }
    section[data-testid="stSidebar"] button {border-radius: 10px !important;}

    /* ---------- Buttons ---------- */
    .stButton > button, .stDownloadButton > button, .stLinkButton > a {
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    /* tombol sekunder (termasuk menu yang tidak aktif): batas & latar terlihat di tema terang maupun gelap */
    .stButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]),
    .stDownloadButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]),
    .stLinkButton > a:not([data-testid="stBaseLinkButton-primary"]) {
        border: 1.5px solid rgba(128,128,128,0.8) !important;
        border: 1.5px solid color-mix(in srgb, currentColor 55%, transparent) !important;
        background: rgba(128,128,128,0.08) !important;
        background: color-mix(in srgb, currentColor 6%, transparent) !important;
    }
    .stButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]):hover,
    .stDownloadButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]):hover,
    .stLinkButton > a:not([data-testid="stBaseLinkButton-primary"]):hover {
        border-color: #2563EB !important;
        background: rgba(37,99,235,0.10) !important;
    }
    .stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"],
    .stDownloadButton > button[kind="primary"], .stDownloadButton > button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #2563EB 0%, #0D9488 100%) !important;
        border: none !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(37,99,235,0.32);
    }
    .stButton > button[kind="primary"] *, .stButton > button[data-testid="stBaseButton-primary"] *,
    .stDownloadButton > button[kind="primary"] *, .stDownloadButton > button[data-testid="stBaseButton-primary"] * {
        color: #ffffff !important;
    }

    /* ---------- Expanders (route cards) ---------- */
    div[data-testid="stExpander"] {
        border-radius: 14px !important;
        border: 1px solid rgba(128,128,128,0.18) !important;
        margin-bottom: 14px;
        overflow: hidden;
    }

    /* ---------- Tabs ---------- */
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        border-radius: 8px 8px 0 0;
    }

    /* ---------- Section headers ---------- */
    .section-header {
        display: flex; align-items: center; gap: 12px;
        margin: 30px 0 14px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid rgba(128,128,128,0.15);
    }
    .section-header .badge {
        width: 36px; height: 36px; border-radius: 10px; flex-shrink: 0;
        background: linear-gradient(135deg, #2563EB 0%, #0D9488 100%);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.05rem;
    }
    .section-header .title {font-weight: 800; font-size: 1.08rem; line-height: 1.3;}
    .section-header .subtitle {font-size: 0.85rem; opacity: 0.9; margin-top: 1px;}

    /* ---------- Empty state ---------- */
    .empty-state {
        border: 1.5px dashed rgba(37,99,235,0.35);
        border-radius: 16px;
        padding: 36px 24px;
        text-align: center;
        background: rgba(37,99,235,0.04);
        margin-top: 8px;
    }
    .empty-state .emoji {font-size: 2.3rem;}
    .empty-state .title {font-weight: 700; font-size: 1.05rem; margin-top: 12px;}
    .empty-state .desc {
        font-size: 0.9rem; opacity: 0.9; margin-top: 4px;
        max-width: 440px; margin-left: auto; margin-right: auto; line-height: 1.5;
    }

    div[data-testid="stSidebarNav"] {display: none;}

    /* ---------- Penanda langkah ---------- */
    .stepper {display: flex; align-items: center; gap: 8px; margin: 4px 0 18px 0;}
    .stepper .step {display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 0.9rem; opacity: 0.85;}
    .stepper .step .dot {
        width: 26px; height: 26px; border-radius: 50%; display: inline-flex; align-items: center;
        justify-content: center; font-size: 0.8rem; border: 2px solid rgba(128,128,128,0.5);
    }
    .stepper .step.active, .stepper .step.done {opacity: 1;}
    .stepper .step.active .dot {background: linear-gradient(135deg, #2563EB 0%, #0D9488 100%); border-color: transparent; color: #fff; box-shadow: 0 0 0 4px rgba(37,99,235,0.22);}
    .stepper .step.done .dot {background: linear-gradient(135deg, #2563EB 0%, #0D9488 100%); border-color: transparent; color: #fff;}
    .stepper .bar {flex: 1 1 16px; height: 2px; background: rgba(128,128,128,0.3); min-width: 12px;}

    /* ---------- Footer (minimalis) ---------- */
    .app-footer {
        margin-top: 48px; padding: 18px 0 4px 0; text-align: center; line-height: 1.5;
        border-top: 1px solid rgba(128,128,128,0.16);
    }
    .app-footer .f-brand {font-weight: 700; font-size: 0.92rem; letter-spacing: 0.02em;}
    .app-footer .f-dev {font-size: 0.8rem; margin-top: 3px; opacity: 0.85;}
    .app-footer .f-name {font-weight: 600;}
    .app-footer .f-heart {color: #ef4444;}

    /* ---------- Tema minimalis ----------
       Satu blok yang menimpa gaya dekoratif di atas: tanpa gradien, bayangan, dan animasi hias.
       Hapus blok ini (sampai akhir CSS) untuk kembali ke tampilan sebelumnya. */
    .stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"],
    .stDownloadButton > button[kind="primary"], .stDownloadButton > button[data-testid="stBaseButton-primary"] {
        background: #2563EB !important; box-shadow: none !important;
    }
    .stButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]),
    .stDownloadButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]),
    .stLinkButton > a:not([data-testid="stBaseLinkButton-primary"]) {
        border: 1px solid rgba(128,128,128,0.45) !important;
        border: 1px solid color-mix(in srgb, currentColor 30%, transparent) !important;
        background: transparent !important;
    }

    .stepper .step.active .dot, .stepper .step.done .dot {background: #2563EB; box-shadow: none;}

    .metric-card {background: transparent; border: 1px solid rgba(128,128,128,0.2); border-radius: 10px; padding: 12px 14px;}
    .metric-card .metric-icon {display: none;}
    .metric-card .metric-label {margin-top: 0; text-transform: none; letter-spacing: 0; font-weight: 500;}
    .metric-card .metric-value {font-size: 1.35rem; font-weight: 700;}

    .section-header {margin: 26px 0 12px 0; padding-bottom: 8px; border-bottom-width: 1px;}
    .section-header .badge {display: none;}
    .section-header .title {font-weight: 700;}

    .empty-state {border: 1px solid rgba(128,128,128,0.2); background: transparent; border-radius: 12px; padding: 26px 20px;}
    .empty-state .emoji {display: none;}
    .empty-state .title {margin-top: 0;}

    div[data-testid="stExpander"] {border-radius: 10px !important; margin-bottom: 10px;}

    .rp-loader {background: transparent; box-shadow: none; border-radius: 12px; border-color: rgba(128,128,128,0.25); padding: 1rem;}
    .rp-bar i {background: #2563EB; animation: none;}
    .rp-indet i {animation: rp-slide 1.5s ease-in-out infinite;}

    /* ---------- Sidebar: lapisan warna biru-hijau tipis di atas warna tema, supaya beda dari area utama (terang & gelap) ---------- */
    section[data-testid="stSidebar"] {
        background-image:
            linear-gradient(90deg, #2563EB, #0D9488),
            linear-gradient(180deg, rgba(37,99,235,0.17) 0%, rgba(13,148,136,0.13) 100%);
        background-size: 100% 3px, 100% 100%; background-repeat: no-repeat;
        border-right: 1px solid rgba(37,99,235,0.28);
        box-shadow: 6px 0 28px rgba(15,23,42,0.08);
    }

    /* ---------- Strip statistik hasil rute ---------- */
    .stat-strip {
        position: relative; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr));
        margin: 6px 0 18px 0; overflow: hidden; border-radius: 18px;
        border: 1px solid rgba(37,99,235,0.2);
        background: linear-gradient(135deg, rgba(37,99,235,0.07), rgba(13,148,136,0.07));
    }
    .stat-strip::before {content: ""; position: absolute; left: 0; right: 0; top: 0; height: 3px; background: linear-gradient(90deg, #2563EB, #0D9488);}
    .stat {position: relative; padding: 20px 22px 18px 22px; animation: statIn 0.6s ease both;}
    .stat:nth-child(2) {animation-delay: 0.08s;} .stat:nth-child(3) {animation-delay: 0.16s;} .stat:nth-child(4) {animation-delay: 0.24s;}
    .stat + .stat {border-left: 1px solid rgba(128,128,128,0.2);}
    .stat-icon {display: inline-grid; place-items: center; width: 30px; height: 30px; border-radius: 50%; font-size: 0.9rem; background: rgba(37,99,235,0.12);}
    .stat-label {margin-top: 10px; font-size: 0.78rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; opacity: 0.85;}
    .stat-line {display: flex; align-items: baseline; gap: 6px; margin-top: 2px; flex-wrap: wrap;}
    .stat-val {
        font-size: clamp(1.6rem, 2.4vw, 2.2rem); font-weight: 800; line-height: 1.15; font-variant-numeric: tabular-nums;
        background: linear-gradient(90deg, #2563EB, #0D9488); -webkit-background-clip: text; background-clip: text;
        color: transparent; -webkit-text-fill-color: transparent;
    }
    .stat-unit {font-size: 0.95rem; font-weight: 600; opacity: 0.8;}
    .stat-sub {margin-top: 2px; font-size: 0.8rem; opacity: 0.85;}
    @keyframes statIn {from {opacity: 0; transform: translateY(6px);} to {opacity: 1; transform: none;}}
    @media (max-width: 720px) {
        .stat-strip {grid-template-columns: repeat(2, minmax(0, 1fr));}
        .stat {padding: 16px 16px 14px 16px;}
        .stat:nth-child(3) {border-left: 0;}
        .stat:nth-child(n+3) {border-top: 1px solid rgba(128,128,128,0.2);}
    }

    /* ---------- Panel perbandingan sebelum vs sesudah ---------- */
    .cmp {
        display: flex; align-items: center; gap: 30px; margin: 4px 0 10px 0; padding: 22px 26px; border-radius: 18px;
        border: 1px solid rgba(37,99,235,0.2); background: linear-gradient(135deg, rgba(37,99,235,0.05), rgba(13,148,136,0.07));
    }
    .cmp-bars {flex: 1 1 auto; min-width: 0; display: grid; gap: 16px;}
    .cmp-row {display: grid; grid-template-columns: 140px minmax(0, 1fr) auto; align-items: center; gap: 14px;}
    .cmp-lbl {font-size: 0.85rem; font-weight: 600; opacity: 0.9;}
    .cmp-track {position: relative; height: 18px; border-radius: 99px; background: rgba(128,128,128,0.14); overflow: hidden;}
    .cmp-track i {
        position: absolute; left: 0; top: 0; bottom: 0; border-radius: 99px; transform-origin: left center;
        animation: cmpGrow 0.9s cubic-bezier(0.22, 1, 0.36, 1) both;
    }
    .cmp-row .cmp-track i.fill {background: #2563EB;}   /* satu warna solid untuk kedua batang: yang dibandingkan hanya panjangnya */
    .cmp-row.opt .cmp-track i {animation-delay: 0.15s;}
    .cmp-row.has-saved .cmp-track i.fill {border-radius: 99px 0 0 99px;}
    .cmp-track i.saved {   /* bagian berarsir = jarak yang berhasil dihemat */
        box-sizing: border-box; border-radius: 0 99px 99px 0; border: 1.5px dashed rgba(13,148,136,0.75); border-left: 0;
        background: repeating-linear-gradient(135deg, rgba(13,148,136,0.38) 0 5px, rgba(13,148,136,0.12) 5px 10px);
        animation: cmpFade 0.7s ease 0.9s both;
    }
    @keyframes cmpFade {from {opacity: 0;} to {opacity: 1;}}
    .cmp-legend {display: flex; align-items: center; gap: 8px; font-size: 0.8rem; opacity: 0.9;}
    .cmp-legend .sw {
        flex: none; width: 22px; height: 10px; border-radius: 3px; border: 1.5px dashed rgba(13,148,136,0.75);
        background: repeating-linear-gradient(135deg, rgba(13,148,136,0.38) 0 4px, rgba(13,148,136,0.12) 4px 8px);
    }
    .cmp-val {min-width: 76px; text-align: right; font-weight: 700; font-variant-numeric: tabular-nums;}
    .cmp-save {flex: none; display: flex; align-items: center; gap: 16px; padding-left: 28px; border-left: 1px solid rgba(128,128,128,0.2);}
    .cmp-ring {position: relative; width: 84px; height: 84px; flex: none;}
    .cmp-ring::before {
        content: ""; position: absolute; inset: 0; border-radius: 50%;
        background: conic-gradient(#0D9488 calc(var(--p) * 1%), rgba(128,128,128,0.2) 0);
        -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 9px), #000 calc(100% - 8px));
        mask: radial-gradient(farthest-side, transparent calc(100% - 9px), #000 calc(100% - 8px));
    }
    .cmp-ring span {position: absolute; inset: 0; display: grid; place-items: center; font-weight: 800; font-size: 1.15rem;}
    .cmp-save-text .big {font-weight: 800; font-size: 1.3rem; line-height: 1.2;}
    .cmp-save-text .small {font-size: 0.82rem; opacity: 0.85; margin-top: 2px; max-width: 190px;}
    @keyframes cmpGrow {from {transform: scaleX(0);} to {transform: scaleX(1);}}
    @media (max-width: 720px) {
        .cmp {flex-direction: column; align-items: stretch; gap: 18px; padding: 18px;}
        .cmp-row {grid-template-columns: 1fr auto;}
        .cmp-track {grid-column: 1 / -1; order: 3;}
        .cmp-save {padding-left: 0; border-left: 0; padding-top: 16px; border-top: 1px solid rgba(128,128,128,0.2);}
    }

    @media (prefers-reduced-motion: reduce) {
        .hero-route, .dev-pulse, .dev-route .n, .stat, .cmp-track i {animation: none !important;}
    }

    /* ---------- Keterbacaan di tema terang & gelap ----------
       Dirancang netral terhadap tema (tanpa mendeteksi tema): tidak ada teks bergradien, garis & permukaan lebih tegas,
       latar halaman dilembutkan oleh lapisan translusen (terasa di tema terang, nyaris tak terasa di tema gelap).
       Hapus blok ini (sampai akhir CSS) untuk kembali ke tampilan sebelumnya. */
    .stApp {background-image: linear-gradient(rgba(71,85,105,0.09), rgba(71,85,105,0.09));}
    [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stMainBlockContainer"], section.main, .main {background: transparent !important;}
    [data-testid="stHeader"] {background: transparent !important; backdrop-filter: blur(8px);}

    /* teks bergradien -> teks warna tema (kontras penuh) + garis gradien di bawahnya */
    .hero-header h1 .grad, .stat-val, .dev-name {
        -webkit-background-clip: border-box; background-clip: border-box;
        -webkit-text-fill-color: currentColor; color: inherit !important;
        background-image: linear-gradient(90deg, #2563EB, #0D9488); background-repeat: no-repeat;
        background-position: left bottom; background-size: 100% 3px; padding-bottom: 3px;
    }
    .dev-name {background-size: 100% 2px; padding-bottom: 2px;}

    /* garis & permukaan lebih tegas + sedikit bayangan (terlihat di tema terang, tak mengganggu di tema gelap) */
    .hero-header, .stat-strip, .cmp {
        border: 1px solid rgba(71,85,105,0.45);
        box-shadow: 0 1px 2px rgba(15,23,42,0.08), 0 8px 22px -10px rgba(15,23,42,0.18);
    }
    .metric-card, .empty-state {border-color: rgba(71,85,105,0.45);}
    .stat + .stat, .cmp-save {border-color: rgba(71,85,105,0.30);}
    .section-header {border-bottom-color: rgba(71,85,105,0.32);}
    .app-footer {border-top-color: rgba(71,85,105,0.32);}
    .rp-loader {border-color: rgba(71,85,105,0.40);}
    .cmp-track {background: rgba(71,85,105,0.24);}
    .cmp-ring::before {background: conic-gradient(#0D9488 calc(var(--p) * 1%), rgba(71,85,105,0.28) 0);}
    section[data-testid="stSidebar"] {border-right-color: rgba(37,99,235,0.42);}
    .dev-badge {background: rgba(71,85,105,0.12);}
    div[data-testid="stExpander"] {border: 1px solid rgba(71,85,105,0.45) !important;}
    div[data-baseweb="input"], div[data-baseweb="select"] > div, div[data-baseweb="textarea"] {border: 1px solid rgba(71,85,105,0.68) !important;}
    div[data-testid="stDataFrame"] {border: 1px solid rgba(71,85,105,0.35); border-radius: 10px; overflow: hidden;}
    .stButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]),
    .stDownloadButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]),
    .stLinkButton > a:not([data-testid="stBaseLinkButton-primary"]) {
        border: 1px solid rgba(71,85,105,0.68) !important;
    }

    /* teks sekunder lebih pekat */
    .hero-header p, .hero-eyebrow, .stepper .step, .stat-label, .stat-unit, .stat-sub, .cmp-lbl,
    .cmp-save-text .small, .cmp-legend, .app-footer .f-dev, .metric-card .metric-label,
    .sidebar-brand .subtitle, .section-header .subtitle, .empty-state, .dev-label, .rp-sub {opacity: 0.94;}
    </style>
    """,
    unsafe_allow_html=True,
)


def loader_html(title, sub="", pct=None):
    """Animasi loading bertema rute (roket melaju melewati titik-titik singgah) + bar progres.
    pct=None → bar berjalan terus (tidak tahu berapa lama); pct 0–1 → bar sesuai kemajuan."""
    t = html_lib.escape(str(title))
    sub_html = f'<div class="rp-sub">{html_lib.escape(str(sub))}</div>' if sub else ""
    if pct is None:
        bar = '<div class="rp-bar rp-indet"><i></i></div>'
    else:
        p = max(0, min(100, int(round(float(pct) * 100))))
        bar = f'<div class="rp-bar"><i style="width:{p}%"></i></div><div class="rp-pct">{p}%</div>'
    return (
        '<div class="rp-loader" role="status" aria-live="polite"><div class="rp-track"><div class="rp-line"></div>'
        '<span class="rp-stop s1"></span><span class="rp-stop s2"></span><span class="rp-stop s3"></span>'
        '<span class="rp-stop s4"></span><div class="rp-rocket" aria-hidden="true"><i class="rp-flame"></i><span>🚀</span></div></div>'
        f'<div class="rp-title">{t}<span class="rp-dots"><b>.</b><b>.</b><b>.</b></span></div>{sub_html}{bar}</div>'
    )


class FancyLoader:
    """Penampil loading yang bisa diperbarui (judul, keterangan, persen) lalu ditutup."""

    def __init__(self, title="Memproses", sub="", pct=None):
        self._slot = st.empty()
        self._title, self._sub, self._pct = title, sub, pct
        self._render()

    def _render(self):
        self._slot.markdown(loader_html(self._title, self._sub, self._pct), unsafe_allow_html=True)

    def update(self, title=None, sub=None, pct=None):
        if title is not None:
            self._title = title
        if sub is not None:
            self._sub = sub
        if pct is not None:
            self._pct = pct
        self._render()

    def close(self):
        self._slot.empty()


@contextlib.contextmanager
def fancy_loading(title="Memproses", sub="", pct=None):
    """Pengganti st.spinner: `with fancy_loading("Judul", "keterangan") as ld:` lalu ld.update(sub=..., pct=...)."""
    ld = FancyLoader(title, sub, pct)
    try:
        yield ld
    finally:
        ld.close()


def metric_card(icon, label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon" aria-hidden="true">{icon}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


HERO_ART = (
    '<svg class="hero-art" viewBox="0 0 220 84" fill="none" aria-hidden="true" focusable="false">'
    '<defs><linearGradient id="heroGrad" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0" stop-color="#2563EB"/><stop offset="1" stop-color="#0D9488"/></linearGradient></defs>'
    '<path class="hero-route" d="M10 68 C 52 68, 56 24, 96 32 S 150 72, 178 42 S 202 20, 210 14" '
    'stroke="url(#heroGrad)" stroke-width="2.6" stroke-linecap="round"/>'
    '<circle cx="10" cy="68" r="5" fill="#2563EB"/><circle cx="96" cy="32" r="5" fill="#2563EB"/>'
    '<circle cx="178" cy="42" r="5" fill="#0D9488"/>'
    '<circle cx="210" cy="14" r="9" fill="#0D9488" fill-opacity="0.2"/><circle cx="210" cy="14" r="5" fill="#0D9488"/>'
    '</svg>'
)


def render_hero(eyebrow, title_plain, title_accent, desc):
    """Banner judul halaman: label kecil, judul dengan satu kata beraksen gradien, deskripsi, dan ilustrasi rute tipis."""
    st.markdown(
        '<div class="hero-header"><div class="hero-text">'
        f'<div class="hero-eyebrow">{html_lib.escape(eyebrow)}</div>'
        f'<h1>{html_lib.escape(title_plain)} <span class="grad">{html_lib.escape(title_accent)}</span></h1>'
        f'<p>{html_lib.escape(desc)}</p></div>{HERO_ART}</div>',
        unsafe_allow_html=True,
    )


def stat_strip(items):
    """Strip statistik: angka besar bergradien, label kecil, keterangan singkat. items = [{icon,label,value,unit,sub}]."""
    cells = []
    for it in items:
        unit = f'<span class="stat-unit">{html_lib.escape(str(it["unit"]))}</span>' if it.get("unit") else ""
        sub = f'<div class="stat-sub">{html_lib.escape(str(it["sub"]))}</div>' if it.get("sub") else ""
        cells.append(
            '<div class="stat">'
            f'<span class="stat-icon" aria-hidden="true">{it["icon"]}</span>'
            f'<div class="stat-label">{html_lib.escape(str(it["label"]))}</div>'
            f'<div class="stat-line"><span class="stat-val">{html_lib.escape(str(it["value"]))}</span>{unit}</div>'
            f'{sub}</div>'
        )
    st.markdown(
        '<div class="stat-strip" role="group" aria-label="Ringkasan hasil rute">' + "".join(cells) + "</div>",
        unsafe_allow_html=True,
    )


def compare_panel(naive_km, opt_km, delta_km, saving_pct):
    """Perbandingan jarak sebelum vs sesudah optimasi: dua bilah sebanding + cincin persen penghematan."""
    top = max(naive_km, opt_km, 0.001)
    w_naive, w_opt = naive_km / top * 100, opt_km / top * 100
    saved_w = max(0.0, w_naive - w_opt) if delta_km > 0.05 else 0.0   # bagian bilah yang "hilang" berkat optimasi
    saved_html = f'<i class="saved" style="left:{w_opt:.1f}%;width:{saved_w:.1f}%"></i>' if saved_w > 0 else ""
    legend = (f'<div class="cmp-legend"><span class="sw"></span>Bagian berarsir = jarak yang dihemat ({delta_km:.1f} km)</div>'
              if saved_w > 0 else "")
    if delta_km > 0.05:
        pct = max(0, min(100, saving_pct))
        side = (
            f'<div class="cmp-save"><div class="cmp-ring" style="--p:{pct:.0f}" aria-hidden="true"><span>{pct:.0f}%</span></div>'
            f'<div class="cmp-save-text"><div class="big">Hemat {delta_km:.1f} km</div>'
            f'<div class="small">{pct:.0f}% lebih singkat dibanding sebelum optimasi</div></div></div>'
        )
    elif delta_km < -0.05:
        side = (
            f'<div class="cmp-save"><div class="cmp-save-text"><div class="big">+{abs(delta_km):.1f} km</div>'
            '<div class="small">lebih panjang dibanding sebelum optimasi</div></div></div>'
        )
    else:
        side = (
            '<div class="cmp-save"><div class="cmp-save-text"><div class="big">≈ sama</div>'
            '<div class="small">urutan awal sudah efisien</div></div></div>'
        )
    st.markdown(
        '<div class="cmp">'
        '<div class="cmp-bars">'
        f'<div class="cmp-row base"><span class="cmp-lbl">Sebelum optimasi</span><div class="cmp-track" aria-hidden="true"><i class="fill" style="width:{w_naive:.1f}%"></i></div><span class="cmp-val">{naive_km:.1f} km</span></div>'
        f'<div class="cmp-row opt{" has-saved" if saved_w > 0 else ""}"><span class="cmp-lbl">Setelah optimasi</span><div class="cmp-track" aria-hidden="true"><i class="fill" style="width:{w_opt:.1f}%"></i>{saved_html}</div><span class="cmp-val">{opt_km:.1f} km</span></div>'
        f'{legend}</div>{side}</div>',
        unsafe_allow_html=True,
    )


def section_header(icon, title, subtitle=None):
    subtitle_html = f'<div class="subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div class="section-header">
            <div class="badge" aria-hidden="true">{icon}</div>
            <div>
                <div class="title" role="heading" aria-level="2">{title}</div>
                {subtitle_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(icon, title, desc):
    st.markdown(
        f"""
        <div class="empty-state">
            <div class="emoji" aria-hidden="true">{icon}</div>
            <div class="title">{title}</div>
            <div class="desc">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


DEV_BADGE_HTML = (
    '<div class="dev-badge">'
    '<div class="dev-top"><span class="dev-avatar" aria-hidden="true">A</span>'
    '<span class="dev-text"><span class="dev-label">Developed by</span><span class="dev-name">Abdillah</span></span></div>'
    '<div class="dev-route" aria-hidden="true"><i class="n n1"></i><i class="n n2"></i><i class="n n3"></i><b class="dev-pulse"></b></div>'
    '</div>'
)


def render_footer():
    year = datetime.date.today().year
    st.markdown(
        f"""
        <div class="app-footer">
            <div class="f-brand">⚡ Routing &amp; Extractor</div>
            <div class="f-dev">Developed with <span class="f-heart">♥</span> by <span class="f-name">Abdillah</span> · © {year}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


ROUTE_COLORS = [
    "#e6194B", "#3cb44b", "#4363d8", "#f58231", "#911eb4",   # 🔴 🟢 🔵 🟠 🟣
    "#ffe119", "#9A6324", "#2b2b2b", "#aab2bd",               # 🟡 🟤 ⚫ ⚪
    "#42d4f4", "#f032e6", "#bfef45", "#fabed4", "#469990",
    "#dcbeff", "#800000", "#aaffc3", "#000075",
]
ROUTE_EMOJIS = ["🔴", "🟢", "🔵", "🟠", "🟣", "🟡", "🟤", "⚫", "⚪"]

# ==========================================================================================
# HELPER FUNCTIONS
# ==========================================================================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def create_distance_matrix(df):
    """Straight-line (haversine) distance matrix in meters — used as the
    fallback when real road data (OSRM) isn't available."""
    n = len(df)
    lat = df["latitude"].to_numpy()
    lon = df["longitude"].to_numpy()
    matrix = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                matrix[i][j] = int(haversine(lat[i], lon[i], lat[j], lon[j]) * 1000)
    return matrix


OSRM_DEFAULT_URL = "https://router.project-osrm.org"
OSRM_DEFAULT_MAX_TABLE = 100  # batas jumlah titik per permintaan di server demo OSRM
FALLBACK_SPEED_KMH = 30  # used only if OSRM is unreachable


def _setting(name, default=None):
    """Baca pengaturan dari st.secrets, lalu environment variable, lalu default."""
    try:
        value = st.secrets.get(name)
    except Exception:
        value = None
    return value or os.environ.get(name) or default


def _osrm_url():
    # Untuk pemakaian serius, arahkan ke server OSRM sendiri lewat Secrets / env var OSRM_BASE_URL.
    return str(_setting("OSRM_BASE_URL", OSRM_DEFAULT_URL)).rstrip("/")


def _osrm_max_table():
    try:
        return max(4, int(_setting("OSRM_MAX_TABLE", OSRM_DEFAULT_MAX_TABLE)))
    except (TypeError, ValueError):
        return OSRM_DEFAULT_MAX_TABLE


def _osrm_request(coords, base_url, sources=None, destinations=None, retries=3):
    """Satu permintaan /table ke OSRM, dengan retry untuk gangguan sementara (429/5xx/timeout)."""
    path = ";".join(f"{lon},{lat}" for lon, lat in coords)
    params = {"annotations": "distance,duration"}
    if sources is not None:
        params["sources"] = ";".join(str(i) for i in sources)
    if destinations is not None:
        params["destinations"] = ";".join(str(i) for i in destinations)

    last_error = None
    for attempt in range(retries):
        try:
            resp = requests.get(f"{base_url}/table/v1/driving/{path}", params=params, timeout=20)
            if resp.status_code in (429, 500, 502, 503, 504):
                raise requests.HTTPError(f"HTTP {resp.status_code}")
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") != "Ok":
                # Kesalahan permintaan (mis. TooBig) — tidak ada gunanya diulang.
                raise ValueError(data.get("message") or data.get("code") or "OSRM mengembalikan error")
            return data["distances"], data["durations"]
        except requests.RequestException as e:
            last_error = e
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
    raise last_error


@st.cache_data(ttl=3600, show_spinner=False, max_entries=64)
def _osrm_matrices_cached(coords, base_url, max_table):
    """Matriks jarak (m) & durasi (detik) dari OSRM, dipecah per blok kalau titiknya melebihi batas server.

    Kegagalan melempar exception, sehingga TIDAK ikut tersimpan di cache.
    """
    n = len(coords)
    dist = [[0] * n for _ in range(n)]
    dur = [[0] * n for _ in range(n)]

    def put(rows, cols, raw_d, raw_t):
        for a, i in enumerate(rows):
            for b, j in enumerate(cols):
                d, t = raw_d[a][b], raw_t[a][b]
                # null = pasangan titik yang tidak bisa dirutekan -> anggap "sangat jauh"
                dist[i][j] = int(d) if d is not None else 10_000_000
                dur[i][j] = t if t is not None else 0

    if n <= max_table:
        raw_d, raw_t = _osrm_request(coords, base_url)
        put(range(n), range(n), raw_d, raw_t)
        return dist, dur

    block = max(2, max_table // 2)
    starts = list(range(0, n, block))
    for i0 in starts:
        rows = list(range(i0, min(i0 + block, n)))
        for j0 in starts:
            cols = list(range(j0, min(j0 + block, n)))
            if i0 == j0:
                raw_d, raw_t = _osrm_request([coords[k] for k in rows], base_url)
            else:
                sub = [coords[k] for k in rows] + [coords[k] for k in cols]
                src = list(range(len(rows)))
                dst = list(range(len(rows), len(rows) + len(cols)))
                raw_d, raw_t = _osrm_request(sub, base_url, src, dst)
            put(rows, cols, raw_d, raw_t)
    return dist, dur


def get_route_matrices(df):
    """Returns (distance_matrix_meters, duration_matrix_seconds, used_real_roads, error_message).

    Memakai OSRM (jalan asli): hasilnya di-cache, titik yang banyak dipecah per blok
    agar tidak melewati batas server, dan gangguan sementara dicoba ulang.
    Kalau tetap gagal, jatuh ke estimasi garis lurus (haversine) dengan kecepatan
    rata-rata tetap, dan alasan kegagalannya ikut dikembalikan supaya bisa ditampilkan.
    """
    n = len(df)
    if n < 2:
        return [[0]], [[0]], True, None

    coords = tuple((round(float(r.longitude), 6), round(float(r.latitude), 6)) for r in df.itertuples())
    try:
        distance_matrix, duration_matrix = _osrm_matrices_cached(coords, _osrm_url(), _osrm_max_table())
        return distance_matrix, duration_matrix, True, None
    except Exception as e:
        distance_matrix = create_distance_matrix(df)
        duration_matrix = [
            [
                (distance_matrix[i][j] / 1000) / FALLBACK_SPEED_KMH * 3600 if i != j else 0
                for j in range(n)
            ]
            for i in range(n)
        ]
        return distance_matrix, duration_matrix, False, str(e)[:160]


def parse_coordinate_text(text):
    """Baca koordinat yang ditempel, mis. '-7.5665, 110.8167' atau '-7,5665; 110,8167'.

    Mengembalikan (lat, lon, pesan_error). pesan_error None kalau berhasil.
    """
    nums = re.findall(r"-?\d+(?:[.,]\d+)?", str(text or ""))
    if len(nums) != 2:
        return None, None, "Tidak terbaca. Tempel dua angka saja, contoh: -7.5665, 110.8167"
    lat, lon = (float(x.replace(",", ".")) for x in nums)
    if not (-90 <= lat <= 90) and (-90 <= lon <= 90) and (-180 <= lat <= 180):
        return None, None, "Latitude di luar rentang. Mungkin urutannya tertukar — format yang benar: latitude, longitude."
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return None, None, "Koordinat di luar rentang valid (latitude -90 s/d 90, longitude -180 s/d 180)."
    return lat, lon, None


def make_sample_csv():
    """Data contoh: 12 merchant fiktif di dua area di sekitar Surakarta."""
    rng = np.random.default_rng(7)
    centers = [(-7.5560, 110.8000), (-7.5700, 110.8350)]
    rows = []
    for i in range(12):
        c = centers[i % 2]
        rows.append(
            {
                "merchant_name": f"Toko Contoh {i + 1:02d}",
                "latitude": round(c[0] + float(rng.normal(0, 0.006)), 6),
                "longitude": round(c[1] + float(rng.normal(0, 0.006)), 6),
            }
        )
    return pd.DataFrame(rows).to_csv(index=False).encode("utf-8-sig")


STEP_LABELS = ["Data", "Pengaturan", "Hasil"]


def render_stepper(slot, done):
    """Penanda langkah. done = jumlah langkah yang sudah selesai (0-3)."""
    items = []
    for i, label in enumerate(STEP_LABELS):
        state = "done" if i < done else ("active" if i == done else "todo")
        mark = "✓" if state == "done" else str(i + 1)
        sr = {"done": " (selesai)", "active": " (langkah saat ini)", "todo": ""}[state]
        cur = ' aria-current="step"' if state == "active" else ""
        items.append(
            f'<div class="step {state}" role="listitem"{cur}><span class="dot" aria-hidden="true">{mark}</span>'
            f'<span class="lbl">{label}</span><span class="sr-only">{sr}</span></div>'
        )
    bar = '<div class="bar" aria-hidden="true"></div>'
    slot.markdown('<div class="stepper" role="list" aria-label="Langkah">' + bar.join(items) + '</div>', unsafe_allow_html=True)


def format_duration_short(seconds):
    """Versi ringkas untuk judul rute: '45 mnt', '1 j 30 mnt'."""
    if seconds is None:
        return "–"
    minutes = round(seconds / 60)
    if minutes < 60:
        return f"{minutes} mnt"
    hours, rem = divmod(minutes, 60)
    return f"{hours} j {rem} mnt" if rem else f"{hours} j"


def route_title(r, emoji):
    """Judul expander rute yang cukup pendek untuk layar HP. Keterangan penuh (estimasi, urutan manual, dst.)
    ada di dalam rute — di judul hanya penanda singkatnya."""
    total = r["duration_sec"] + r.get("visit_sec", 0) + r.get("wait_sec", 0)
    head = f"{emoji} Rute {r['route_id'] + 1}"
    if r.get("tanggal"):
        petugas = str(r.get("petugas") or "")
        if len(petugas) > 14:
            petugas = petugas[:13] + "…"
        head += f" · {fmt_day_label(datetime.date.fromisoformat(r['tanggal']))} · {petugas}"
    elif r.get("petugas"):
        petugas = str(r["petugas"])
        if len(petugas) > 14:
            petugas = petugas[:13] + "…"
        head += f" · {petugas}" + (f" · Hari {r['hari_ke']}" if (r.get("hari_ke") or 1) > 1 else "")
    title = f"{head} · {len(r['df'])} titik · {r['distance_km']:.1f} km · {format_duration_short(total)}"
    if not r.get("real_roads", True):
        title += " ⚠️"
    if r.get("manual"):
        title += " ✏️"
    return title


def route_needs_check(r):
    """Rute yang sebaiknya dicek: memakai estimasi garis lurus, atau ada kunjungan di luar jam operasional."""
    return (not r.get("real_roads", True)) or bool(r.get("n_outside_hours"))


def route_matches(r, q):
    """Cocok dengan pencarian: nomor rute ('3' / 'rute 3'), nama petugas, atau nama merchant di rute itu. Kosong = semua."""
    q = (q or "").strip().casefold()
    if not q:
        return True
    q_num = re.sub(r"^rute\s*", "", q)
    if q_num.isdigit() and int(q_num) == r["route_id"] + 1:
        return True
    if q in str(r.get("petugas") or "").casefold() or q in str(r.get("driver") or "").casefold():
        return True
    return bool(r["df"]["merchant_name"].astype(str).str.casefold().str.contains(q, regex=False).any())


def search_routes(routes, q):
    """Saring rute menurut pencarian. Angka (atau 'rute 3') dibaca sebagai nomor rute selama rute itu ada;
    kalau tidak ada rute bernomor itu, dicari sebagai teks (nama merchant/petugas).
    Return (daftar_rute, dicari_lewat_nomor)."""
    q = (q or "").strip().casefold()
    if not q:
        return list(routes), False
    q_num = re.sub(r"^rute\s*", "", q)
    if q_num.isdigit():
        by_no = [r for r in routes if r["route_id"] + 1 == int(q_num)]
        if by_no:
            return by_no, True
    return [r for r in routes if route_matches(r, q)], False


def _md_escape(text):
    """Escape karakter markdown pada teks dari data pengguna (nama merchant) sebelum masuk st.caption/st.markdown."""
    return re.sub(r"([\\`*_{}\[\]()#+\-.!|<>~$])", r"\\\1", str(text))


def find_merchant_hits(route_summaries, q, limit=8):
    """Merchant yang namanya memuat q -> ([(nama, nomor_rute, urutan), ...][:limit], total_cocok)."""
    q = (q or "").strip().casefold()
    hits = []
    if not q:
        return hits, 0
    for r in route_summaries:
        df = r["df"]
        mask = df["merchant_name"].astype(str).str.casefold().str.contains(q, regex=False)
        for _, row in df[mask].iterrows():
            seq = int(row["sequence"]) if "sequence" in df.columns and pd.notna(row["sequence"]) else None
            hits.append((str(row["merchant_name"]), r["route_id"] + 1, seq))
    return hits[:limit], len(hits)


def format_duration(seconds):
    if seconds is None:
        return "–"
    minutes = round(seconds / 60)
    if minutes < 60:
        return f"{minutes} menit"
    hours, rem = divmod(minutes, 60)
    return f"{hours} jam {rem} menit" if rem else f"{hours} jam"


def solve_tsp(distance_matrix, round_trip=False, fixed_start=False):
    """Urutan kunjungan optimal dengan OR-Tools.

    - round_trip=True : rute melingkar, kembali ke titik pertama (indeks 0).
    - round_trip=False, fixed_start=True : mulai di indeks 0 (titik awal), selesai di mana saja.
    - round_trip=False, fixed_start=False: mulai & selesai di mana saja (titik terbaik).

    Untuk rute satu arah dipakai node "dummy" berjarak 0 ke/dari semua titik, supaya
    solver tidak menghitung perjalanan pulang yang sebenarnya tidak dilakukan.
    Mengembalikan daftar indeks node asli (tanpa dummy, tanpa titik kembali).
    """
    n = len(distance_matrix)
    if n <= 2:
        return list(range(n))

    if round_trip:
        matrix = distance_matrix
        manager = pywrapcp.RoutingIndexManager(n, 1, 0)
    else:
        # tambah node dummy (indeks n) dengan jarak 0 ke/dari semua node
        matrix = [list(row) + [0] for row in distance_matrix] + [[0] * (n + 1)]
        if fixed_start:
            manager = pywrapcp.RoutingIndexManager(n + 1, 1, [0], [n])
        else:
            manager = pywrapcp.RoutingIndexManager(n + 1, 1, n)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.time_limit.seconds = 5
    solution = routing.SolveWithParameters(search_parameters)

    if solution is None:
        return list(range(n))

    route = []
    index = routing.Start(0)
    while not routing.IsEnd(index):
        node = manager.IndexToNode(index)
        if node < n:  # lewati node dummy
            route.append(node)
        index = solution.Value(routing.NextVar(index))
    return route


def route_leg_sum(matrix, order, round_trip=False):
    """Jumlah jarak/waktu sepanjang urutan; kalau round_trip, termasuk kaki pulang ke titik pertama."""
    path = list(order) + ([order[0]] if round_trip and len(order) > 1 else [])
    return sum(matrix[path[i]][path[i + 1]] for i in range(len(path) - 1))


# ---------- Merchant prioritas ----------
TRUTHY_STRINGS = {"ya", "yes", "y", "true", "1", "benar", "prioritas", "penting", "high"}


def is_truthy(val):
    """Dipakai untuk kolom opsional 'prioritas' — menerima berbagai cara orang
    menulis "ya" (termasuk angka 1, True, 'Yes', dst) di Excel/CSV."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val == 1
    return str(val).strip().lower() in TRUTHY_STRINGS


def _submatrix(matrix, indices):
    return [[matrix[i][j] for j in indices] for i in indices]


def solve_tsp_with_priority(distance_matrix, priority_idx, other_idx, has_start, round_trip):
    """Urutan kunjungan yang mengunjungi SEMUA titik `priority_idx` lebih dulu
    (diurutkan efisien di antara sesamanya), baru lanjut ke titik lainnya.

    Pendekatan dua-tahap (bukan pemrograman batasan penuh): tahap 1
    menyelesaikan TSP kecil untuk [titik awal]+prioritas, tahap 2 melanjutkan
    dari titik prioritas terakhir ke sisa titik. round_trip (kembali ke
    titik awal) hanya diterapkan di tahap akhir. Mengembalikan daftar indeks
    asli, format sama seperti hasil solve_tsp() biasa — jadi kompatibel
    langsung dengan finalize_route().
    """
    n = len(distance_matrix)
    if not priority_idx or n <= 2:
        return solve_tsp(distance_matrix, round_trip=round_trip, fixed_start=has_start)

    start_part = [0] if has_start else []
    phase1_idx = start_part + list(priority_idx)
    if len(phase1_idx) <= 1:
        phase1_order = phase1_idx
    else:
        sub_order = solve_tsp(_submatrix(distance_matrix, phase1_idx), round_trip=False, fixed_start=has_start)
        phase1_order = [phase1_idx[i] for i in sub_order]

    if not other_idx:
        return phase1_order

    last_priority = phase1_order[-1] if phase1_order else 0
    phase2_idx = [last_priority] + list(other_idx)
    sub_order2 = solve_tsp(_submatrix(distance_matrix, phase2_idx), round_trip=round_trip, fixed_start=True)
    phase2_order = [phase2_idx[i] for i in sub_order2]

    return (phase1_order[:-1] + phase2_order) if phase1_order else phase2_order


# ---------- Optimasi urutan berdasarkan jam operasional (time window) ----------
TW_LATE_PENALTY = 100   # biaya per detik lewat jam tutup (satuan = meter jarak) → 1 menit telat ≈ 6 km "hukuman"
TW_WAIT_COST = 2        # biaya per detik menunggu toko buka → 30 menit menunggu ≈ 3,6 km jarak


def build_time_windows(route_df, start_dt, base_date, has_start):
    """{indeks_baris: (buka_detik|None, tutup_detik|None)} relatif terhadap jam mulai rute.
    Baris tanpa jam operasional tidak dimasukkan; titik awal (kalau ada) dilewati."""
    windows = {}
    for i in range(len(route_df)):
        if has_start and i == 0:
            continue
        row = route_df.iloc[i]
        jb, jt = _parse_hhmm(row.get("jam_buka")), _parse_hhmm(row.get("jam_tutup"))
        if jb is None and jt is None:
            continue
        lo = (datetime.datetime.combine(base_date, jb) - start_dt).total_seconds() if jb else None
        hi = (datetime.datetime.combine(base_date, jt) - start_dt).total_seconds() if jt else None
        if lo is not None and hi is not None and hi <= lo:
            hi += 86400   # buka lewat tengah malam
        windows[i] = (lo, hi)
    return windows


def solve_tsp_time_windows(distance_matrix, duration_matrix, windows, visit_sec,
                           round_trip=False, first_is_start=False):
    """Urutan kunjungan yang meminimalkan jarak SAMBIL tiba saat merchant buka.

    - Belum buka saat rute sampai → solver mengunjungi merchant lain dulu; kalau tidak ada yang lain, petugas
      menunggu sampai buka (jadwal akhir memakai aturan yang sama: jam tiba = jam buka).
    - Lewat jam tutup bersifat "lunak": kalau mustahil dipenuhi semua, solver memilih urutan dengan pelanggaran
      terkecil — bukan gagal. Merchant yang tutup lebih awal otomatis didahulukan. Return daftar indeks (format sama
    seperti solve_tsp) atau None kalau solver tidak menghasilkan solusi."""
    try:
        return _solve_tsp_time_windows(distance_matrix, duration_matrix, windows, visit_sec,
                                       round_trip, first_is_start)
    except Exception:
        return None   # jangan sampai membuat app error — pemanggil jatuh ke urutan jarak biasa


def _solve_tsp_time_windows(distance_matrix, duration_matrix, windows, visit_sec, round_trip, first_is_start):
    n = len(distance_matrix)
    if n <= 2 or not windows:
        return None
    if round_trip:
        dm, tm = distance_matrix, duration_matrix
        manager = pywrapcp.RoutingIndexManager(n, 1, 0)
    else:
        dm = [list(r) + [0] for r in distance_matrix] + [[0] * (n + 1)]
        tm = [list(r) + [0] for r in duration_matrix] + [[0] * (n + 1)]
        if first_is_start:
            manager = pywrapcp.RoutingIndexManager(n + 1, 1, [0], [n])
        else:
            manager = pywrapcp.RoutingIndexManager(n + 1, 1, n)
    routing = pywrapcp.RoutingModel(manager)

    def dist_cb(fi, ti):
        return int(dm[manager.IndexToNode(fi)][manager.IndexToNode(ti)])

    def time_cb(fi, ti):
        a, b = manager.IndexToNode(fi), manager.IndexToNode(ti)
        service = 0 if (a >= n or (a == 0 and first_is_start)) else int(visit_sec)
        return int(tm[a][b]) + service

    routing.SetArcCostEvaluatorOfAllVehicles(routing.RegisterTransitCallback(dist_cb))
    # slack = waktu tunggu (boleh sampai 24 jam); menunggu "berbiaya" supaya solver lebih suka mengunjungi
    # merchant lain dulu daripada diam menunggu.
    routing.AddDimension(routing.RegisterTransitCallback(time_cb), 86400, 10 * 86400, True, "Time")
    time_dim = routing.GetDimensionOrDie("Time")
    time_dim.SetSlackCostCoefficientForAllVehicles(TW_WAIT_COST)
    for node, (lo, hi) in windows.items():
        idx = manager.NodeToIndex(node)
        if lo is not None and lo > 0:
            time_dim.CumulVar(idx).SetMin(int(lo))   # belum buka -> harus menunggu / datang nanti
        if hi is not None:
            time_dim.SetCumulVarSoftUpperBound(idx, max(0, int(hi)), TW_LATE_PENALTY)

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.seconds = 1 if n <= 6 else (3 if n <= 15 else 5)
    solution = routing.SolveWithParameters(params)
    if solution is None:
        return None
    route, index = [], routing.Start(0)
    while not routing.IsEnd(index):
        node = manager.IndexToNode(index)
        if node < n:
            route.append(node)
        index = solution.Value(routing.NextVar(index))
    return route


# ---------- Multi-depot ----------
def parse_depot_rows(rows):
    """rows: list (nama, link_atau_koordinat) dari form titik-awal dinamis di UI.
    Mengembalikan (list_depot_dict, list_pesan_error). Baris dengan lokasi
    kosong dilewati tanpa dianggap error (baris belum diisi, bukan salah isi)."""
    depots, errors = [], []
    for i, (name_raw, loc_raw) in enumerate(rows, start=1):
        loc_part = str(loc_raw or "").strip()
        name = str(name_raw or "").strip()
        if not loc_part:
            continue
        lat = lon = None
        if "http" not in loc_part.lower():
            lat, lon, _err = parse_coordinate_text(loc_part)
        if lat is None:
            parsed_name, lat, lon = extract_google_maps_data(loc_part)
            if not name:
                name = parsed_name or f"Titik Awal Rute {i}"
        if not name:
            name = f"Titik Awal Rute {i}"
        if lat is None or lon is None:
            errors.append(f"Titik awal Rute {i} ({name}): link/koordinat tidak dikenali — rute ini dimulai otomatis.")
            continue
        depots.append({"name": name, "lat": lat, "lon": lon, "row": i - 1})
    return depots, errors


def nearest_depot_index(depots, lat, lon):
    best_i, best_dist = 0, float("inf")
    for i, d in enumerate(depots):
        dist = haversine(lat, lon, d["lat"], d["lon"])
        if dist < best_dist:
            best_i, best_dist = i, dist
    return best_i


def assign_routes_to_depots(df, depots):
    """Pasangkan tiap rute hasil pengelompokan dengan titik awal yang diisi pengguna.

    df: kolom route/latitude/longitude. depots: list dict {name, lat, lon, row}; `row` = nomor baris
    titik awal (0 = Rute 1, dst). Pasangan dipilih dengan total jarak (pusat rute → titik awal) terpendek,
    lalu rute diberi nomor baru sesuai baris titik awalnya — jadi "Rute k" memang dimulai dari titik awal
    yang diisi di baris k. Rute yang tidak kebagian titik awal mengisi nomor yang masih kosong dan tidak
    punya titik awal khusus. Mengembalikan ({label_lama: label_baru}, {label_baru: depot atau None})."""
    ids = sorted(df["route"].unique())
    cents = {
        rid: (float(g["latitude"].mean()), float(g["longitude"].mean()))
        for rid, g in df.groupby("route")
    }
    cost = [[haversine(cents[rid][0], cents[rid][1], d["lat"], d["lon"]) for d in depots] for rid in ids]
    match = {}  # label lama -> posisi depot
    try:
        from scipy.optimize import linear_sum_assignment
        rows, cols = linear_sum_assignment(cost)
        for r_i, c_i in zip(rows, cols):
            match[ids[int(r_i)]] = int(c_i)
    except Exception:
        # Tanpa scipy: tiap titik awal (berurutan) mengambil rute terdekat yang masih bebas.
        free_r = list(range(len(ids)))
        for d_i in range(len(depots)):
            if not free_r:
                break
            r_i = min(free_r, key=lambda k: cost[k][d_i])
            match[ids[r_i]] = d_i
            free_r.remove(r_i)
    new_of, depot_of, taken = {}, {}, set()
    for rid, d_pos in match.items():
        slot = int(depots[d_pos]["row"])
        new_of[rid] = slot
        depot_of[slot] = depots[d_pos]
        taken.add(slot)
    nxt = 0
    for rid in ids:
        if rid in new_of:
            continue
        while nxt in taken:
            nxt += 1
        new_of[rid] = nxt
        depot_of[nxt] = None
        taken.add(nxt)
    return new_of, depot_of


# ---------- Pembagian petugas & hari kerja (petugas × hari kerja) ----------
ID_DAYS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
ID_DAYS_SHORT = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]


def make_work_dates(start_date, weekdays, n):
    """n tanggal kerja berurutan mulai start_date; hanya hari yang ada di `weekdays` (0 = Senin … 6 = Minggu)."""
    out, d, guard = [], start_date, 0
    if not weekdays:
        return out
    while len(out) < n and guard < 3700:
        if d.weekday() in weekdays:
            out.append(d)
        d += datetime.timedelta(days=1)
        guard += 1
    return out


def fmt_day_label(d, short=True):
    """'Sen 26 Okt' (atau 'Senin 26 Oktober')."""
    mon = _ID_MONTHS[d.month - 1]
    if short:
        return f"{ID_DAYS_SHORT[d.weekday()]} {d.day} {mon[:3]}"
    return f"{ID_DAYS[d.weekday()]} {d.day} {mon}"


def _xy_arr(lat, lon):
    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)
    k = math.cos(math.radians(float(np.nanmean(lat)))) if len(lat) else 1.0
    return np.column_stack([lon * k, lat]), k


def _cap_balance(xy, labels, cap):
    """Pastikan tiap kelompok ≤ cap: titik kelebihan dipindah ke kelompok terdekat yang masih muat."""
    labels = np.array(labels, dtype=int)
    k = int(labels.max()) + 1 if len(labels) else 0
    for _ in range(len(labels) * 2 + 5):
        sizes = np.bincount(labels, minlength=k)
        over = [c for c in range(k) if sizes[c] > cap]
        if not over:
            break
        c = over[0]
        under = [j for j in range(k) if sizes[j] < cap and sizes[j] > 0]
        if not under:
            under = [j for j in range(k) if sizes[j] < cap]
        if not under:
            break
        cent = {j: xy[labels == j].mean(axis=0) for j in range(k) if sizes[j] > 0}
        own = cent[c]
        best, best_cost = None, float("inf")
        for i in np.where(labels == c)[0]:
            d_own = float(np.linalg.norm(xy[i] - own))
            for j in under:
                tgt = cent.get(j, xy[i])
                cost = float(np.linalg.norm(xy[i] - tgt)) - d_own
                if cost < best_cost:
                    best, best_cost = (i, j), cost
        labels[best[0]] = best[1]
    return labels


def _assign_territories(xy, kscale, n_petugas, starts, assigned, seed=42):
    """Wilayah tiap petugas: indeks petugas (0..P-1) untuk setiap merchant."""
    n, P = len(xy), n_petugas
    start_xy = [None if s is None else np.array([s[1] * kscale, s[0]]) for s in starts]
    if assigned is not None and (assigned >= 0).any():  # wilayah dikunci: pakai penugasan yang ada
        terr = np.array(assigned, dtype=int)
        anchors = {p: xy[terr == p].mean(axis=0) for p in range(P) if (terr == p).any()}
        for i in np.where(terr < 0)[0]:
            terr[i] = min(anchors, key=lambda p: float(np.linalg.norm(xy[i] - anchors[p])))
        return terr
    k = max(1, min(P, n))
    lab = KMeans(n_clusters=k, random_state=seed, n_init=10).fit_predict(xy) if k > 1 else np.zeros(n, dtype=int)
    lab = _cap_balance(xy, lab, math.ceil(n / k * 1.25))
    cents = {c: xy[lab == c].mean(axis=0) for c in range(k) if (lab == c).any()}
    cl_ids = sorted(cents)
    petugas_for, used = {}, set()
    with_start = [p for p in range(P) if start_xy[p] is not None]
    if with_start and cl_ids:
        cost = [[float(np.linalg.norm(cents[c] - start_xy[p])) for p in with_start] for c in cl_ids]
        try:
            from scipy.optimize import linear_sum_assignment
            rows, cols = linear_sum_assignment(cost)
            pairs = list(zip(rows, cols))
        except Exception:
            pairs, free_c = [], list(range(len(cl_ids)))
            for j in range(len(with_start)):
                if not free_c:
                    break
                i = min(free_c, key=lambda a: cost[a][j])
                pairs.append((i, j))
                free_c.remove(i)
        for i, j in pairs:
            petugas_for[cl_ids[int(i)]] = with_start[int(j)]
            used.add(with_start[int(j)])
    free_p = [p for p in range(P) if p not in used]
    rest = sorted((c for c in cl_ids if c not in petugas_for), key=lambda c: cents[c][0])  # barat → timur
    for c, p in zip(rest, free_p):
        petugas_for[c] = p
    return np.array([petugas_for[c] for c in lab], dtype=int)


def plan_multi_day(lat, lon, n_petugas, cap, starts=None, assigned=None, seed=42):
    """Bagi merchant ke petugas (wilayah) lalu ke hari kunjungan.

    starts: list titik awal tiap petugas [(lat, lon) | None]. assigned: array indeks petugas per merchant
    (-1 = belum ditugaskan) untuk wilayah terkunci. Tiap (petugas, hari) menjadi satu rute berisi ≤ cap merchant,
    hari-hari seorang petugas disusun berurutan dari yang terdekat ke titik awalnya (area bersebelahan di hari berdekatan).
    Mengembalikan (label_rute per merchant, [{"route_id", "p", "day"}]) — rute diurutkan per hari lalu petugas."""
    n = len(lat)
    P = max(1, int(n_petugas))
    cap = max(1, int(cap))
    starts = list(starts or [])
    starts += [None] * (P - len(starts))
    xy, kscale = _xy_arr(lat, lon)
    terr = _assign_territories(xy, kscale, P, starts, assigned, seed)
    day = np.zeros(n, dtype=int)
    for p in range(P):
        idx = np.where(terr == p)[0]
        if len(idx) == 0:
            continue
        R = math.ceil(len(idx) / cap)
        if R <= 1:
            sub = np.zeros(len(idx), dtype=int)
        else:
            sub = KMeans(n_clusters=R, random_state=seed, n_init=10).fit_predict(xy[idx])
            sub = _cap_balance(xy[idx], sub, math.ceil(len(idx) / R))  # ukuran hari dibuat merata (≤ cap)
        labs = sorted(set(sub.tolist()))
        cents = {l: xy[idx][sub == l].mean(axis=0) for l in labs}
        cur = None if starts[p] is None else np.array([starts[p][1] * kscale, starts[p][0]])
        order, remaining = [], set(labs)
        if cur is None:
            first = min(remaining, key=lambda l: cents[l][0])
            order.append(first)
            remaining.discard(first)
            cur = cents[first]
        while remaining:
            nxt = min(remaining, key=lambda l: float(np.linalg.norm(cents[l] - cur)))
            order.append(nxt)
            remaining.discard(nxt)
            cur = cents[nxt]
        day_of = {l: d for d, l in enumerate(order)}
        day[idx] = [day_of[l] for l in sub]
    keys = sorted(set(zip(day.tolist(), terr.tolist())))
    rid = {key: i for i, key in enumerate(keys)}
    labels = np.array([rid[(d, p)] for d, p in zip(day.tolist(), terr.tolist())], dtype=int)
    meta = [{"route_id": i, "day": d, "p": p} for (d, p), i in rid.items()]
    meta.sort(key=lambda m: m["route_id"])
    return labels, meta


def build_schedule_matrix(route_summaries):
    """Tabel jadwal: baris = petugas, kolom = tanggal, isi = 'N titik · X km'. None kalau bukan pembagian petugas & hari kerja."""
    rows = [r for r in route_summaries if r.get("tanggal")]
    if not rows:
        rows = [r for r in route_summaries if r.get("petugas") and r.get("hari_ke")]
        if not rows or max(r["hari_ke"] for r in rows) < 2:
            return None   # tanpa tanggal & hanya satu hari: tidak perlu tabel jadwal
        cols = sorted({r["hari_ke"] for r in rows})
        names = list(dict.fromkeys(r["petugas"] for r in rows))
        data = {f"Hari {c}": {} for c in cols}
        for r in rows:
            data[f"Hari {r['hari_ke']}"][r["petugas"]] = f"{len(r['df']) - (1 if r.get('has_start') else 0)} titik · {r['distance_km']:.0f} km"
        mat = pd.DataFrame(data).reindex(index=names, columns=[f"Hari {c}" for c in cols]).fillna("—")
        mat.index.name = "Petugas"
        return mat
    cols = sorted({r["tanggal"] for r in rows})
    names = []
    for r in rows:
        if r.get("petugas") not in names:
            names.append(r.get("petugas"))
    lab = {c: fmt_day_label(datetime.date.fromisoformat(c)) for c in cols}
    data = {lab[c]: {} for c in cols}
    for r in rows:
        data[lab[r["tanggal"]]][r["petugas"]] = f"{len(r['df']) - (1 if r.get('has_start') else 0)} titik · {r['distance_km']:.0f} km"
    mat = pd.DataFrame(data).reindex(index=names, columns=[lab[c] for c in cols]).fillna("—")
    mat.index.name = "Petugas"
    return mat


# ---------- Jam operasional (time windows) ----------
def _parse_hhmm(val):
    """Baca 'HH:MM' (atau datetime.time/Timestamp) jadi datetime.time; None kalau gagal/kosong."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    if isinstance(val, datetime.time):
        return val
    if isinstance(val, datetime.datetime):
        return val.time()
    s = str(val).strip()
    if not s or s.lower() == "nan":
        return None
    m = re.match(r"^(\d{1,2})[:.](\d{2})", s)
    if not m:
        return None
    h, mi = int(m.group(1)), int(m.group(2))
    if 0 <= h <= 23 and 0 <= mi <= 59:
        return datetime.time(h, mi)
    return None


def check_time_window(arrival_dt, jam_buka, jam_tutup):
    """Bandingkan jam tiba dengan jam operasional. Mengembalikan status pendek
    ("" kalau tidak ada jam operasional / tepat waktu) untuk ditampilkan di
    tabel, PDF, dan WhatsApp."""
    open_t, close_t = _parse_hhmm(jam_buka), _parse_hhmm(jam_tutup)
    if open_t is None and close_t is None:
        return ""
    t = arrival_dt.time()
    if open_t and close_t and close_t <= open_t:
        # buka lewat tengah malam (mis. 18:00–02:00): di luar jam hanya kalau jatuh di celah siang
        if close_t < t < open_t:
            return f"⚠️ tiba sebelum buka ({open_t.strftime('%H:%M')})"
        return "✅"
    if open_t and t < open_t:
        return f"⚠️ tiba sebelum buka ({open_t.strftime('%H:%M')})"
    if close_t and t > close_t:
        return f"⚠️ tiba setelah tutup ({close_t.strftime('%H:%M')})"
    return "✅"


# Batas titik singgah (waypoints) di link Google Maps menurut dokumentasi resmi:
# maks. 9 di desktop/aplikasi, tapi hanya 3 di browser HP. Kalau lebih, titik
# singgah berlebih DIBUANG diam-diam oleh Google Maps — makanya rute dipecah.
MAPS_MAX_WAYPOINTS_DESKTOP = 9
MAPS_MAX_WAYPOINTS_MOBILE = 3


def generate_google_maps_links(df, max_waypoints, from_my_location=False):
    """Pecah rute jadi beberapa link Google Maps.

    Tiap link berisi origin + maksimal `max_waypoints` titik singgah + destination.
    Link berikutnya dimulai dari titik akhir link sebelumnya, sehingga urutan tetap
    tersambung. Mengembalikan list (indeks_awal, indeks_akhir, url) — indeks 0-based
    pada baris df.

    from_my_location=True: TIAP link tanpa origin, sehingga Google Maps memakai posisi pengguna saat link itu
    dibuka ("Lokasi Anda"). Rute dipotong jadi bagian yang tidak saling tumpang-tindih (maks. max_waypoints + 1
    merchant per link; merchant terakhir bagian = tujuan, sisanya titik singgah).
    """
    coords = [f"{row.latitude},{row.longitude}" for _, row in df.iterrows()]
    links = []
    if from_my_location:
        size = max_waypoints + 1
        for start in range(0, len(coords), size):
            seg = coords[start:start + size]
            url = f"https://www.google.com/maps/dir/?api=1&destination={seg[-1]}"
            if len(seg) > 1:
                url += "&waypoints=" + "%7C".join(seg[:-1])
            links.append((start, start + len(seg) - 1, url + "&travelmode=driving"))
        return links
    if len(coords) < 2:
        return []
    step = max_waypoints + 1
    start = 0
    while start < len(coords) - 1:
        end = min(start + step, len(coords) - 1)
        seg = coords[start:end + 1]
        url = (
            f"https://www.google.com/maps/dir/?api=1&origin={seg[0]}&destination={seg[-1]}"
        )
        if len(seg) > 2:
            url += "&waypoints=" + "%7C".join(seg[1:-1])
        url += "&travelmode=driving"
        links.append((start, end, url))
        start = end
    return links


def stop_nav_url(lat, lon):
    """Link navigasi ke SATU titik dari posisi pengguna saat ini (tanpa origin), langsung mulai navigasi di aplikasi."""
    return f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}&travelmode=driving&dir_action=navigate"


SHORT_LINK_DOMAINS = ("maps.app.goo.gl", "goo.gl/maps", "app.goo.gl")


def search_nominatim(query, limit=8):
    """Free OpenStreetMap place search — no API key needed. Coverage of
    small/local merchants in Indonesia is thinner than Google, so this is
    best used with a specific name plus a city/area hint.

    Returns (results, error_message). error_message is None on a normal
    request (even if it legitimately found zero places) and is set only
    when the request itself failed — e.g. the public Nominatim server
    rate-limited us (it's free but usage-capped) or the network timed out
    — so the UI can tell "genuinely no match" apart from "couldn't even
    ask", which previously both looked like a plain empty result.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "jsonv2",
        "addressdetails": 1,
        "namedetails": 1,  # gives the place's own OSM "name" tag — needed to
                           # tell apart results that share a generic search
                           # term (e.g. several "SPBU" with different codes)
        "limit": limit,
        "countrycodes": "id",
    }
    # Nominatim's usage policy requires a real identifying User-Agent.
    headers = {"User-Agent": "RutePipelineOptimizerApp/1.0 (streamlit-community-app)"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=8)
        if resp.status_code == 429:
            return [], "Layanan pencarian sedang dibatasi (terlalu banyak permintaan). Coba lagi dalam beberapa detik."
        if resp.status_code == 403:
            return [], "Layanan pencarian menolak permintaan ini (kemungkinan dibatasi sementara). Coba lagi nanti."
        resp.raise_for_status()
        return resp.json(), None
    except requests.exceptions.Timeout:
        return [], "Layanan pencarian tidak merespons (timeout). Coba lagi."
    except requests.exceptions.RequestException:
        return [], "Gagal menghubungi layanan pencarian — periksa koneksi internet, lalu coba lagi."
    except Exception:
        return [], "Terjadi kesalahan tak terduga saat mencari. Coba lagi."


def nominatim_result_name(result, fallback_query=""):
    """Picks the most specific name available for a Nominatim result, so
    that results sharing a generic search term (e.g. several "SPBU") stay
    distinguishable instead of all being saved under the same name.

    Priority: the place's own OSM name tag > the first segment of its full
    address string (usually the specific place name) > the search term the
    user typed > a generic placeholder.
    """
    namedetails = result.get("namedetails") or {}
    specific_name = namedetails.get("name") or namedetails.get("name:id")
    if specific_name:
        return specific_name.strip()

    display_name = result.get("display_name", "")
    if display_name:
        first_segment = display_name.split(",")[0].strip()
        if first_segment:
            return first_segment

    return fallback_query.strip() or "Lokasi"


def resolve_short_link(link):
    """maps.app.goo.gl / goo.gl links don't contain coordinates in the text
    itself — the real URL only appears after following the redirect."""
    if not any(domain in link for domain in SHORT_LINK_DOMAINS):
        return link
    try:
        resp = requests.head(link, allow_redirects=True, timeout=6)
        if resp.url and resp.url != link:
            return resp.url
    except Exception:
        pass
    try:
        resp = requests.get(link, allow_redirects=True, timeout=6)
        return resp.url or link
    except Exception:
        return link


def extract_google_maps_data(link):
    """Returns (place_name_or_None, latitude_or_None, longitude_or_None)."""
    try:
        link = resolve_short_link(link.strip())

        # --- Coordinates -----------------------------------------------
        # A "data=" segment can hold MULTIPLE "!8m2!3d<lat>!4d<lon>" pairs:
        # when Google can't pin an unofficial/small place precisely, it
        # first embeds a nearby *landmark's* own block — recognizable by an
        # explicit "!2s<Landmark Name>" right before its "!8m2" — purely to
        # anchor the search, then appends the actual target's block last
        # (with no "!2sName", since the target's name is already in the
        # URL path). Taking the FIRST match (or the "@lat,lng" viewport,
        # which mirrors that same landmark) grabs the wrong location, so we
        # take the LAST pair instead — that's always the real target.
        all_pin_pairs = re.findall(r"!8m2!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", link)
        # Priority 2: a bare "q=lat,lng" or "query=lat,lng" parameter.
        query_coord_match = re.search(r"[?&](?:q|query)=(-?\d+\.\d+),(-?\d+\.\d+)", link)
        # Priority 3: any generic "!3d...!4d..." pair (same last-wins logic).
        all_generic_pairs = re.findall(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", link)
        # Priority 4 (least reliable): the "@lat,lng,zoom" viewport center —
        # as shown above this can actually be a disambiguation landmark's
        # coordinates rather than the place itself, so it's only used when
        # nothing else in the link gives us a coordinate at all.
        view_match = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", link)

        latitude = longitude = None
        if all_pin_pairs:
            latitude, longitude = float(all_pin_pairs[-1][0]), float(all_pin_pairs[-1][1])
        elif query_coord_match:
            latitude, longitude = float(query_coord_match.group(1)), float(query_coord_match.group(2))
        elif all_generic_pairs:
            latitude, longitude = float(all_generic_pairs[-1][0]), float(all_generic_pairs[-1][1])
        elif view_match:
            latitude, longitude = float(view_match.group(1)), float(view_match.group(2))

        # --- Place name --------------------------------------------------
        place_name = None
        place_match = re.search(r"/place/([^/@]+)", link)
        if place_match:
            place_name = unquote(place_match.group(1)).replace("+", " ").strip()
        else:
            query_name_match = re.search(r"[?&]query=([^&]+)", link)
            if query_name_match:
                candidate = unquote(query_name_match.group(1)).replace("+", " ").strip()
                # Skip it if it's actually just coordinates, not a name.
                if not re.fullmatch(r"-?\d+\.\d+,-?\d+\.\d+", candidate):
                    place_name = candidate

        return place_name, latitude, longitude
    except Exception:
        return None, None, None


def balance_clusters(df, max_points_per_route):
    df = df.copy()
    for _guard in range(1000):  # pengaman supaya tidak pernah macet
        cluster_sizes = df["route"].value_counts().to_dict()
        oversized_clusters = [c for c, size in cluster_sizes.items() if size > max_points_per_route]
        if not oversized_clusters:
            break

        for big_cluster in oversized_clusters:
            excess_points = cluster_sizes[big_cluster] - max_points_per_route
            big_cluster_df = df[df["route"] == big_cluster]
            candidate_clusters = [c for c, size in cluster_sizes.items() if size < max_points_per_route]
            if not candidate_clusters:
                break

            for _ in range(excess_points):
                candidate_clusters = [c for c, size in cluster_sizes.items() if size < max_points_per_route]
                if not candidate_clusters:
                    break
                best_point_index, best_target_cluster = None, None
                best_distance = float("inf")
                for idx, row in big_cluster_df.iterrows():
                    for target_cluster in candidate_clusters:
                        target_df = df[df["route"] == target_cluster]
                        target_centroid_lat = target_df["latitude"].mean()
                        target_centroid_lon = target_df["longitude"].mean()
                        dist = haversine(row["latitude"], row["longitude"], target_centroid_lat, target_centroid_lon)
                        if dist < best_distance:
                            best_distance = dist
                            best_point_index = idx
                            best_target_cluster = target_cluster
                if best_point_index is not None:
                    df.loc[best_point_index, "route"] = best_target_cluster
                    cluster_sizes[big_cluster] -= 1
                    cluster_sizes[best_target_cluster] += 1
                    big_cluster_df = df[df["route"] == big_cluster]
    return df


def fill_clusters(df, max_points_per_route):
    """Bagi titik jadi rute yang diisi PENUH sesuai maksimal (mis. 16 titik, maks 10 -> 10 + 6).

    Tiap rute dibangun dengan cara: ambil titik terluar dari sisa titik sebagai
    awal, lalu tambahkan terus titik terdekat dari pusat kelompok sampai penuh.
    Rute-rute awal biasanya rapat; rute terakhir berisi sisa (bisa lebih tersebar).
    Mengembalikan array label rute (0, 1, 2, ...) berurutan sesuai indeks df.
    """
    coords = df[["latitude", "longitude"]].to_numpy(dtype=float)
    n = len(coords)
    labels = np.full(n, -1, dtype=int)
    remaining = list(range(n))
    route_id = 0
    while remaining:
        pts = coords[remaining]
        center = pts.mean(axis=0)
        seed_pos = int(np.argmax(((pts - center) ** 2).sum(axis=1)))
        group = [remaining.pop(seed_pos)]
        while len(group) < max_points_per_route and remaining:
            gc = coords[group].mean(axis=0)
            rem_pts = coords[remaining]
            nearest = int(np.argmin(((rem_pts - gc) ** 2).sum(axis=1)))
            group.append(remaining.pop(nearest))
        labels[group] = route_id
        route_id += 1
    return labels


def _max_points_control(df):
    """Slider 'maksimal titik per rute' (dipakai di mode Desktop & Mobile)."""
    slider_max = max(2, len(df))
    if slider_max <= 2:
        # st.slider needs min_value < max_value; with only 2
        # merchants there's only one sensible route anyway.
        metric_card("📍", "Maksimal titik per rute", slider_max)
        return slider_max
    return st.slider(
        "Maksimal titik per rute", min_value=2, max_value=slider_max,
        value=slider_max,
        help="Default = total merchant, sehingga semua muat dalam 1 rute. Geser ke bawah untuk memecah jadi beberapa rute.",
    )


def _plan_control(df, plan_mode):
    """Kontrol penentu jumlah rute. Mengembalikan (maks_titik_per_rute, jumlah_rute_atau_None)."""
    n = len(df)
    if plan_mode == PLAN_COUNT:
        k_max = max(1, n)
        k_val = min(max(1, int(st.session_state.target_routes_flag)), k_max)
        k = st.number_input(
            "Jumlah rute",
            min_value=1, max_value=k_max, value=k_val, step=1,
            key=_wk("_target_widget"), on_change=_sync_target,
            help="Misalnya 5 sales = 5 rute. Merchant dibagi merata menurut area lokasi.",
        )
        return math.ceil(n / int(k)), int(k)
    return _max_points_control(df), None


def validate_dataframe(df):
    """Returns (is_valid, list_of_error_messages)."""
    errors = []
    required_cols = ["merchant_name", "latitude", "longitude"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        errors.append(f"Kolom wajib hilang: {', '.join(missing)}")
        return False, errors

    if df.empty:
        errors.append("File tidak berisi data.")
        return False, errors

    numeric_lat = pd.to_numeric(df["latitude"], errors="coerce")
    numeric_lon = pd.to_numeric(df["longitude"], errors="coerce")

    def _blank(series):
        return series.isna() | series.astype(str).str.strip().isin(["", "nan", "None", "NaT"])

    # Baris dengan latitude DAN longitude sama-sama kosong bukan error: koordinatnya
    # nanti dicari otomatis dari nama/alamat (lihat handle_missing_coordinates).
    both_blank = _blank(df["latitude"]) & _blank(df["longitude"])
    bad_rows = df[(numeric_lat.isna() | numeric_lon.isna()) & ~both_blank]
    if not bad_rows.empty:
        errors.append(
            f"{len(bad_rows)} baris memiliki latitude/longitude yang tidak valid (bukan angka, "
            "atau hanya salah satunya yang terisi)."
        )

    out_of_range = df[
        (numeric_lat < -90) | (numeric_lat > 90) | (numeric_lon < -180) | (numeric_lon > 180)
    ]
    if not out_of_range.empty:
        errors.append(f"{len(out_of_range)} baris memiliki koordinat di luar rentang valid.")

    empty_names = df[df["merchant_name"].isna() | (df["merchant_name"].astype(str).str.strip() == "")]
    if not empty_names.empty:
        errors.append(f"{len(empty_names)} baris tidak memiliki merchant_name.")

    return len(errors) == 0, errors


REQUIRED_COLS = ("merchant_name", "latitude", "longitude")
# Kolom opsional: kalau ada, dipakai otomatis untuk fitur prioritas & jam operasional.
OPTIONAL_COLS = ("prioritas", "jam_buka", "jam_tutup", "alamat", "status")
NORMALIZE_COLS = REQUIRED_COLS + OPTIONAL_COLS


# ---- Impor data dari link Google Sheet --------------------------------------------------------------------
SHEET_MAX_BYTES = 10 * 1024 * 1024
_SHEET_RE = re.compile(r"^https?://docs\.google\.com/spreadsheets/d/(e/)?([A-Za-z0-9_-]{20,})")


def parse_sheet_link(link):
    """Link Google Sheet -> (id, gid_atau_None, diterbitkan_ke_web) atau None bila bukan link Google Sheet."""
    m = _SHEET_RE.match((link or "").strip())
    if not m:
        return None
    gid = re.search(r"[#&?]gid=(\d+)", link)
    return m.group(2), (gid.group(1) if gid else None), bool(m.group(1))


def fetch_google_sheet_csv(link, getter=None):
    """Unduh satu tab Google Sheet sebagai CSV. Return (ok, bytes_atau_pesan_galat, nama_file).
    URL unduhan dibuat sendiri dari ID yang sudah divalidasi (tidak pernah mengambil alamat sembarang dari pengguna)."""
    parsed = parse_sheet_link(link)
    if parsed is None:
        return False, ("Itu bukan link Google Sheet. Buka sheet-nya lalu salin link dari address bar, bentuknya "
                       "https://docs.google.com/spreadsheets/d/…/edit. (File Excel di Google Drive tidak didukung; "
                       "unduh lalu upload, atau buka dengan Google Sheets.)"), ""
    sid, gid, published = parsed
    if published:
        url = f"https://docs.google.com/spreadsheets/d/e/{sid}/pub?output=csv" + (f"&gid={gid}" if gid else "")
    else:
        url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv" + (f"&gid={gid}" if gid else "")
    getter = getter or requests.get
    try:
        r = getter(url, timeout=(5, 20), stream=True, allow_redirects=True, headers={"User-Agent": "Mozilla/5.0 (routing-app)"})
    except Exception as e:
        return False, f"Tidak bisa terhubung ke Google Sheets ({type(e).__name__}). Coba lagi sebentar.", ""
    host = (urllib.parse.urlparse(str(getattr(r, "url", url))).hostname or "").lower()
    if not (host == "docs.google.com" or host.endswith(".googleusercontent.com")):
        return False, ("Sheet ini tidak bisa dibaca tanpa login. Buka Sheet → Bagikan → Akses umum → "
                       "**Siapa saja yang memiliki link** (Pelihat), lalu coba lagi."), ""
    if r.status_code in (401, 403):
        return False, "Sheet tidak dibagikan. Buka Sheet → Bagikan → **Siapa saja yang memiliki link** (Pelihat), lalu coba lagi.", ""
    if r.status_code == 404:
        return False, "Sheet tidak ditemukan. Periksa linknya (atau nomor tab #gid=…).", ""
    if r.status_code != 200:
        return False, f"Google Sheets menolak permintaan (HTTP {r.status_code}).", ""
    ctype = (r.headers.get("Content-Type") or "").lower()
    chunks, total = [], 0
    for ch in r.iter_content(65536):
        total += len(ch)
        if total > SHEET_MAX_BYTES:
            return False, f"Sheet terlalu besar (> {SHEET_MAX_BYTES // (1024 * 1024)} MB).", ""
        chunks.append(ch)
    data = b"".join(chunks)
    head = data[:200].lstrip().lower()
    if "html" in ctype or head.startswith(b"<!doctype") or head.startswith(b"<html"):
        return False, ("Sheet belum bisa dibaca tanpa login. Buka Sheet → Bagikan → Akses umum → "
                       "**Siapa saja yang memiliki link** (Pelihat), lalu coba lagi."), ""
    if not data.strip():
        return False, "Sheet (tab ini) kosong.", ""
    return True, data, f"GoogleSheet-{sid[:6]}-{gid or 'tab1'}.csv"


SHEET_SYNC_SECONDS = 30      # jeda pengecekan otomatis


def sheet_sync_start(ss, link, fname, data):
    """Muat data Sheet ke daftar file dan mulai pantau perubahannya."""
    ss.uploaded_store[fname] = data
    ss.sheet_link_saved = link.strip()
    ss.sheet_sync = {"link": link.strip(), "fname": fname, "hash": hashlib.sha256(data).hexdigest(), "on": True,
                     "checked": None, "changed": None, "error": None, "pending": None}


def _sheet_conflict(ss, fname):
    """'edits' = ada edit tabel tersimpan pada baris Sheet ini (kuncinya berbasis nomor baris, bisa salah sasaran bila baris
    bergeser); 'pending' = ada perubahan di editor tabel yang belum diterapkan; None = aman diperbarui."""
    pre = fname + "#"
    ed = ss.get("data_edits") or {}
    if any(str(k).startswith(pre) for k in ed.get("deleted", [])) or any(str(k).startswith(pre) for k in ed.get("changed", {})):
        return "edits"
    stt = ss.get(f"data_editor_{ss.get('data_edit_nonce', 0)}")
    if isinstance(stt, dict) and any(stt.get(k) for k in ("edited_rows", "added_rows", "deleted_rows")):
        return "pending"
    return None


def sheet_sync_apply(ss, data, now, drop_edits=False):
    sy = ss.sheet_sync
    if drop_edits:
        pre = sy["fname"] + "#"
        ed = ss.data_edits
        ed["deleted"] = [k for k in ed.get("deleted", []) if not str(k).startswith(pre)]
        ed["changed"] = {k: v for k, v in ed.get("changed", {}).items() if not str(k).startswith(pre)}
    ss.uploaded_store[sy["fname"]] = data
    sy.update(hash=hashlib.sha256(data).hexdigest(), changed=now, pending=None, error=None)
    ss.data_edit_nonce = ss.get("data_edit_nonce", 0) + 1       # editor tabel dimuat ulang dengan data baru


def sheet_sync_check(ss, now, fetcher=None):
    """Satu kali pengecekan. Return: 'off' | 'error' | 'same' | 'conflict' | 'applied'."""
    sy = ss.get("sheet_sync")
    if not sy or not sy.get("on"):
        return "off"
    if sy["fname"] not in ss.uploaded_store:      # file dihapus pengguna: berhenti memantau
        ss.sheet_sync = None
        return "off"
    ok, data, _ = (fetcher or fetch_google_sheet_csv)(sy["link"])
    sy["checked"] = now
    if not ok:
        sy["error"] = data
        return "error"
    sy["error"] = None
    if hashlib.sha256(data).hexdigest() == sy["hash"]:
        sy["pending"] = None
        return "same"
    kind = _sheet_conflict(ss, sy["fname"])
    if kind:
        sy["pending"] = (data, kind)
        return "conflict"
    sheet_sync_apply(ss, data, now)
    return "applied"


SHEET_WRITE_ID_COL = "merchant_id"
_SHEET_WRITE_URL_RE = re.compile(r"^https://script\.google\.com/macros/s/[A-Za-z0-9_\-]+/exec$")


def sheet_write_config():
    """(url, secret) penulisan balik ke Sheet dari secrets/env, atau None bila belum diatur / URL tidak valid."""
    url = str(_setting("SHEET_WRITE_URL", "") or "").strip()
    secret = str(_setting("SHEET_WRITE_SECRET", "") or "").strip()
    if not url or not secret or not _SHEET_WRITE_URL_RE.match(url):
        return None
    return url, secret


def sheet_write_build(fname, data, edits):
    """Ubah edit tabel pada satu file Sheet menjadi (updates, df_baru, dilewati).
    updates = [{"id": merchant_id, "values": {kolom: nilai}}]; baris diidentifikasi lewat kolom merchant_id (bukan nomor baris).
    dilewati = jumlah baris yang tidak punya ID. Baris yang dihapus di tabel TIDAK dihapus dari Sheet."""
    df = read_table_file(fname, data)
    idc = next((c for c in df.columns if str(c).strip().lower() == SHEET_WRITE_ID_COL), None)
    if idc is None:
        raise ValueError(f"Sheet tidak punya kolom {SHEET_WRITE_ID_COL}.")
    pre = fname + "#"
    updates, skipped = [], 0
    new_df = df.copy()
    for key, cols in (edits.get("changed") or {}).items():
        if not str(key).startswith(pre):
            continue
        try:
            i = int(str(key)[len(pre):])
        except ValueError:
            continue
        if not 0 <= i < len(df):
            continue
        rid = df.iloc[i][idc]
        if pd.isna(rid) or str(rid).strip() == "":
            skipped += 1
            continue
        if isinstance(rid, float) and rid.is_integer():
            rid = int(rid)
        vals = {}
        for c, v in cols.items():
            if isinstance(v, float) and math.isnan(v):
                v = ""
            vals[c] = v
            if c not in new_df.columns:
                new_df[c] = None
            new_df[c] = new_df[c].astype(object)
            new_df.iloc[i, new_df.columns.get_loc(c)] = v
        if vals:
            updates.append({"id": str(rid), "values": vals})
    return updates, new_df, skipped


def sheet_write_post(cfg, updates, poster=None):
    """Kirim ke Apps Script Web App. Return (ok, pesan_atau_hasil)."""
    url, secret = cfg
    try:
        r = (poster or requests.post)(url, data=json.dumps({"secret": secret, "updates": updates}),
                                      headers={"Content-Type": "text/plain"}, timeout=60)
    except Exception as e:
        return False, f"Tidak bisa menghubungi Apps Script ({type(e).__name__}). Cek URL Web App dan koneksi."
    try:
        res = r.json()
    except Exception:
        txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(getattr(r, "text", "") or ""))).strip()[:160]
        return False, (f"Jawaban Apps Script bukan JSON (status {getattr(r, 'status_code', '?')}): \"{txt}\". "
                       "Biasanya akses Web App belum 'Anyone', skrip belum diterbitkan ulang (New version), atau skrip error; "
                       "cek menu Executions di Apps Script.")
    if not isinstance(res, dict) or not res.get("ok"):
        return False, f"Ditolak Apps Script: {(res or {}).get('error', 'jawaban tidak dikenali') if isinstance(res, dict) else 'jawaban tidak dikenali'}"
    return True, res


KOBO_MAX_ROWS = 20000
_KOBO_SERVER_RE = re.compile(r"^https://[a-z0-9\-]+\.kobotoolbox\.org$")
_KOBO_UID_RE = re.compile(r"^[A-Za-z0-9]{10,40}$")
KOBO_STATUS_MAP = {"prospek": "prospek", "sedang_pendekatan": "sedang pendekatan",
                   "sudah_akuisisi": "sudah akuisisi", "belum_tertarik": "belum tertarik", "tidak_ditemukan": "tidak ditemukan"}


KOBO_HASIL_CHOICES = [
    ("sudah_akuisisi", "Sudah akuisisi"),
    ("penjadwalan_ulang", "Penjadwalan ulang"),
    ("belum_bertemu_pic", "Belum bertemu PIC"),
    ("merchant_tidak_ditemukan", "Merchant tidak ditemukan"),
    ("belum_tertarik", "Belum tertarik"),
    ("sudah_memiliki_produk", "Sudah memiliki produk"),
]
# Hasil kunjungan -> status di aplikasi. 'merchant_tidak_ditemukan' -> "tidak ditemukan" (tidak dirutekan lagi).
KOBO_HASIL_STATUS = {"sudah_akuisisi": "sudah akuisisi", "belum_tertarik": "belum tertarik",
                     "merchant_tidak_ditemukan": "tidak ditemukan",
                     "sudah_memiliki_produk": "belum tertarik",
                     "penjadwalan_ulang": "sedang pendekatan", "belum_bertemu_pic": "sedang pendekatan"}


def kobo_config():
    """(server, token, asset_uid) dari secrets/env, atau None bila belum diatur / tidak valid."""
    server = str(_setting("KOBO_SERVER", "https://kf.kobotoolbox.org") or "").strip().rstrip("/")
    token = str(_setting("KOBO_TOKEN", "") or "").strip()
    uid = str(_setting("KOBO_ASSET_UID", "") or "").strip()
    if not _KOBO_SERVER_RE.match(server) or not token or not _KOBO_UID_RE.match(uid):
        return None
    return server, token, uid


def _norm_id(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return ""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v).strip()


def kobo_choice_labels(cfg, list_name="merchant", getter=None):
    """{nilai_pilihan: label} dari isi formulir yang di-deploy di Kobo (mis. merchant_id -> nama merchant). {} bila gagal."""
    server, token, uid = cfg
    try:
        r = (getter or requests.get)(f"{server}/api/v2/assets/{uid}.json",
                                     headers={"Authorization": f"Token {token}", "Accept": "application/json"}, timeout=60)
        r.raise_for_status()
        choices = (r.json().get("content") or {}).get("choices") or []
    except Exception:
        return {}
    out = {}
    for c in choices:
        if not isinstance(c, dict) or str(c.get("list_name") or c.get("list_name_id") or "") != list_name:
            continue
        lab = c.get("label")
        if isinstance(lab, dict):
            lab = next(iter(lab.values()), "")
        if isinstance(lab, (list, tuple)):
            lab = lab[0] if lab else ""
        if lab not in (None, ""):
            out[_norm_id(c.get("name"))] = re.sub(r"\s+", " ", str(lab)).strip()
    return out


def kobo_fetch(cfg, getter=None):
    """Ambil semua isian formulir dari API KoboToolbox. Return (ok, DataFrame_atau_pesan)."""
    server, token, uid = cfg
    get = getter or requests.get
    rows, start, page = [], 0, 1000
    try:
        while len(rows) < KOBO_MAX_ROWS:
            r = get(f"{server}/api/v2/assets/{uid}/data.json",
                    params={"limit": page, "start": start, "sort": json.dumps({"_id": 1})},
                    headers={"Authorization": f"Token {token}", "Accept": "application/json"}, timeout=60)
            if r.status_code in (401, 403):
                return False, "KoboToolbox menolak akses: cek KOBO_TOKEN dan izin akun pada proyek ini."
            if r.status_code == 404:
                return False, "Proyek tidak ditemukan: cek KOBO_ASSET_UID dan KOBO_SERVER (server global atau eu)."
            r.raise_for_status()
            res = r.json()
            chunk = res.get("results") if isinstance(res, dict) else None
            if not isinstance(chunk, list):
                return False, "Jawaban KoboToolbox tidak dikenali."
            rows.extend(c for c in chunk if isinstance(c, dict))
            if len(chunk) < page:
                break
            start += page
    except Exception as e:
        return False, f"Tidak bisa menghubungi KoboToolbox ({type(e).__name__})."
    return True, pd.DataFrame(rows)


def _kobo_latlon(row):
    """(lat, lon) lokasi kunjungan dari isian geopoint ('lat lon alt akurasi') atau _geolocation; (None, None) bila tak ada."""
    txt = row.get("lokasi_kunjungan")
    if isinstance(txt, str):
        parts = txt.split()
        if len(parts) >= 2:
            try:
                la, lo = float(parts[0]), float(parts[1])
                if -90 <= la <= 90 and -180 <= lo <= 180:
                    return la, lo
            except ValueError:
                pass
    g = row.get("_geolocation")
    if isinstance(g, (list, tuple)) and len(g) >= 2 and all(isinstance(v, (int, float)) for v in g[:2]):
        if -90 <= g[0] <= 90 and -180 <= g[1] <= 180:
            return float(g[0]), float(g[1])
    return None, None


def _kobo_foto_url(row):
    atts = row.get("_attachments")
    if not isinstance(atts, list):
        return ""
    pick = None
    for a in atts:
        if isinstance(a, dict) and str(a.get("question_xpath", "")).split("/")[-1] == "foto_kunjungan":
            pick = a
            break
    if pick is None:
        pick = next((a for a in atts if isinstance(a, dict)), None)
    if not pick:
        return ""
    url = str(pick.get("download_large_url") or pick.get("download_url") or "")
    return url if url.startswith("https://") else ""


KOBO_LATEST_COLS = ["merchant_id", "hasil_kunjungan", "status_baru", "petugas", "_submission_time",
                    "lat_kunjungan", "lon_kunjungan", "foto_url"]


def kobo_latest(df):
    """Kunjungan terbaru per merchant_id. Return DataFrame dengan KOBO_LATEST_COLS (kosong bila tak ada isian)."""
    if df is None or df.empty or "merchant_id" not in df.columns:
        return pd.DataFrame(columns=KOBO_LATEST_COLS)
    d = df.copy()
    for c in ("hasil_kunjungan", "status_baru", "petugas", "_submission_time"):
        if c not in d.columns:
            d[c] = ""
    d["merchant_id"] = d["merchant_id"].map(_norm_id)
    d = d[d["merchant_id"] != ""]
    ll = d.apply(_kobo_latlon, axis=1) if len(d) else []
    d["lat_kunjungan"] = [x[0] for x in ll]
    d["lon_kunjungan"] = [x[1] for x in ll]
    d["foto_url"] = d.apply(_kobo_foto_url, axis=1) if len(d) else []
    d = d.sort_values("_submission_time", kind="stable").drop_duplicates("merchant_id", keep="last")
    return d[KOBO_LATEST_COLS].reset_index(drop=True)


def kobo_view(latest, merchants_df=None, labels=None):
    """Tabel tampilan hasil kunjungan: waktu (WIB), petugas, nama merchant (dicocokkan lewat merchant_id), hasil, jarak
    kunjungan dari titik merchant (m), tautan lokasi & foto. Terbaru di atas."""
    cols = ["Waktu", "Petugas", "Merchant", "Hasil kunjungan", "Jarak dari titik (m)", "Lokasi", "Foto"]
    if latest is None or latest.empty:
        return pd.DataFrame(columns=cols)
    look = {}
    if merchants_df is not None and not merchants_df.empty:
        idc = next((c for c in merchants_df.columns if str(c).strip().lower() == SHEET_WRITE_ID_COL), None)
        if idc is not None:
            for _, r in merchants_df.iterrows():
                look.setdefault(_norm_id(r[idc]), (str(r.get("merchant_name", "") or "").strip(), r.get("latitude"), r.get("longitude")))
    hasil_lbl = dict(KOBO_HASIL_CHOICES)
    t = pd.to_datetime(latest["_submission_time"], utc=True, errors="coerce")
    waktu = t.dt.tz_convert("Asia/Jakarta").dt.strftime("%d/%m/%Y %H:%M").fillna("")
    rows = []
    for i, r in latest.iterrows():
        nm, mla, mlo = look.get(r["merchant_id"], ("", None, None))
        nm = (labels or {}).get(r["merchant_id"]) or nm
        la, lo = r["lat_kunjungan"], r["lon_kunjungan"]
        has_v = la is not None and lo is not None and not pd.isna(la) and not pd.isna(lo)
        dist = None
        try:
            if has_v and mla is not None and mlo is not None and not pd.isna(mla) and not pd.isna(mlo):
                dist = int(round(haversine(float(la), float(lo), float(mla), float(mlo)) * 1000))
        except (TypeError, ValueError):
            dist = None
        rows.append({
            "Waktu": waktu.iloc[i], "_t": t.iloc[i],
            "Petugas": str(r["petugas"] or ""),
            "Merchant": nm or f"ID {r['merchant_id']}",
            "Hasil kunjungan": hasil_lbl.get(str(r["hasil_kunjungan"]), str(r["hasil_kunjungan"] or "")),
            "Jarak dari titik (m)": dist,
            "Lokasi": f"https://www.google.com/maps?q={la:.6f},{lo:.6f}" if has_v else None,
            "Foto": r["foto_url"] or None,
        })
    out = pd.DataFrame(rows).sort_values("_t", ascending=False, na_position="last").drop(columns=["_t"])
    return out[cols].reset_index(drop=True)


def kobo_status_updates(latest, sheet_df):
    """Status dari Kobo yang berbeda dari Sheet -> (updates, df_sheet_baru, jumlah_id_tak_dikenal)."""
    idc = next((c for c in sheet_df.columns if str(c).strip().lower() == SHEET_WRITE_ID_COL), None)
    if idc is None or "status" not in sheet_df.columns:
        raise ValueError("Sheet perlu kolom merchant_id dan status.")
    pos = {_norm_id(v): i for i, v in enumerate(sheet_df[idc])}
    new_df = sheet_df.copy()
    new_df["status"] = new_df["status"].astype(object)
    updates, unknown = [], 0
    for _, r in latest.iterrows():
        st_new = KOBO_STATUS_MAP.get(str(r.get("status_baru", "")).strip()) or \
            KOBO_HASIL_STATUS.get(str(r.get("hasil_kunjungan", "")).strip())
        if not st_new:
            continue
        i = pos.get(r["merchant_id"])
        if i is None:
            unknown += 1
            continue
        cur = sheet_df.iloc[i]["status"]
        if (str(cur).strip().lower() if not pd.isna(cur) else "") == st_new:
            continue
        updates.append({"id": r["merchant_id"], "values": {"status": st_new}})
        new_df.iloc[i, new_df.columns.get_loc("status")] = st_new
    return updates, new_df, unknown


def build_xlsform(df, title="Kunjungan Merchant", filter_by_petugas=True, include_excluded=False, extra_petugas=()):
    """Buat XLSForm (bytes .xlsx) untuk KoboToolbox dari data merchant.
    Pilihan merchant: nilai internal = merchant_id (tersimpan di hasil, tidak ditampilkan), label = nama merchant.
    Return (bytes, info) dengan info = {merchants, petugas, filtered, generated_ids, warnings}."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    from openpyxl.utils import get_column_letter

    warnings = []
    d = df.copy()
    if not include_excluded and "status" in d.columns:
        d = d[~d["status"].astype(str).str.strip().str.lower().isin(STATUS_EXCLUDED)]
    idc = next((c for c in d.columns if str(c).strip().lower() == SHEET_WRITE_ID_COL), None)
    pc = next((c for c in d.columns if str(c).strip().lower() == "petugas"), None)
    ac = next((c for c in d.columns if str(c).strip().lower() == "alamat"), None)

    def _clean(v):
        return "" if v is None or (isinstance(v, float) and math.isnan(v)) else re.sub(r"\s+", " ", str(v)).strip()

    petugas_vals = sorted({_clean(v) for v in d[pc]} - {""}, key=str.lower) if pc else []
    _have = {v.lower() for v in petugas_vals}
    for v in extra_petugas:                      # nama petugas tambahan yang diketik manual
        v = _clean(v)[:60]
        if v and v.lower() not in _have:
            petugas_vals.append(v)
            _have.add(v.lower())
    petugas_vals = sorted(petugas_vals, key=str.lower)
    merchants, seen_ids, generated, dup_ids, no_name = [], set(), idc is None, 0, 0
    for n, (_, r) in enumerate(d.iterrows(), start=1):
        name = _clean(r.get("merchant_name"))
        if not name:
            no_name += 1
            continue
        mid = _norm_id(r[idc]) if idc is not None else f"M{n:04d}"
        if not mid:
            mid = f"M{n:04d}"
            generated = True
        mid = mid.replace(" ", "_") if re.search(r"\s", mid) else mid
        if mid in seen_ids:
            dup_ids += 1
            continue
        seen_ids.add(mid)
        merchants.append({"id": mid, "name": name, "alamat": _clean(r.get(ac)) if ac else "", "petugas": _clean(r[pc]) if pc else ""})
    # nama kembar dibedakan lewat alamat (atau 2 baris pertama alamat), bukan lewat ID
    from collections import Counter
    cnt = Counter(m["name"].lower() for m in merchants)
    for m in merchants:
        m["label"] = m["name"]
        if cnt[m["name"].lower()] > 1:
            m["label"] = f"{m['name']} - {m['alamat'][:40]}" if m["alamat"] else f"{m['name']} ({m['id']})"
    if generated:
        warnings.append("Data tidak punya kolom merchant_id (atau ada yang kosong): ID dibuat otomatis (M0001, M0002, …). "
                        "ID ini tidak ada di Google Sheet, jadi hasil kunjungan belum bisa dicocokkan ke Sheet. Tambahkan kolom merchant_id di Sheet dulu.")
    if dup_ids:
        warnings.append(f"{dup_ids} baris dilewati karena merchant_id kembar.")
    if no_name:
        warnings.append(f"{no_name} baris dilewati karena tanpa nama merchant.")
    if len(merchants) > 3000:
        warnings.append("Lebih dari 3.000 merchant: formulir bisa lambat di ponsel. Pertimbangkan membagi per petugas atau per wilayah.")
    if not merchants:
        raise ValueError("Tidak ada merchant yang bisa dimasukkan ke formulir.")
    filtered = bool(filter_by_petugas and pc and any(m["petugas"] for m in merchants))

    survey_h = ["type", "name", "label", "required", "choice_filter", "appearance"]
    survey = [
        ("start", "start", "", "", "", ""), ("end", "end", "", "", "", ""),
        ("today", "tanggal", "", "", "", ""), ("deviceid", "device", "", "", "", ""),
        (("select_one petugas" if petugas_vals else "text"), "petugas", "Nama petugas", "yes", "", "minimal" if petugas_vals else ""),
        ("select_one merchant", "merchant_id", "Nama merchant", "yes", "petugas=${petugas} or petugas=''" if filtered else "", "autocomplete"),
        ("select_one hasil", "hasil_kunjungan", "Hasil kunjungan", "yes", "", "minimal"),
        ("geopoint", "lokasi_kunjungan", "Lokasi kunjungan (ambil sebelum foto)", "yes", "", ""),
        ("image", "foto_kunjungan", "Foto kunjungan (ambil langsung dengan kamera)", "yes", "", "new"),   # new = hanya kamera, tanpa galeri
    ]
    choices_h = ["list_name", "name", "label", "petugas"]
    choices = [("petugas", v, v, "") for v in petugas_vals]
    choices += [("hasil", k, lbl, "") for k, lbl in KOBO_HASIL_CHOICES]
    choices += [("merchant", m["id"], m["label"], m["petugas"] if filtered else "") for m in merchants]

    wb = Workbook()

    def put(ws, header, rows, widths):
        ws.append(header)
        for row in rows:
            ws.append(list(row))
        for c in ws[1]:
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor="2563EB")
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
        ws.freeze_panes = "A2"

    ws = wb.active
    ws.title = "survey"
    put(ws, survey_h, survey, [22, 20, 26, 10, 36, 14])
    put(wb.create_sheet("choices"), choices_h, choices, [16, 24, 40, 20])
    slug = re.sub(r"[^a-z0-9_]+", "_", title.lower()).strip("_") or "kunjungan_merchant"
    put(wb.create_sheet("settings"), ["form_title", "form_id", "version", "default_language"],
        [(title[:100], slug[:40], datetime.datetime.now().strftime("%Y%m%d%H%M"), "Indonesian (id)")], [30, 28, 16, 20])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue(), {"merchants": len(merchants), "petugas": len(petugas_vals), "filtered": filtered,
                            "generated_ids": generated, "warnings": warnings}


def read_table_file(name, data):
    """Baca file .xlsx atau .csv menjadi DataFrame.

    CSV: pemisah (koma / titik koma / tab) dideteksi otomatis, BOM UTF-8 ditangani.
    Nama kolom wajib dinormalkan (huruf kecil, tanpa spasi tepi) dan koma desimal pada
    latitude/longitude (format Indonesia, mis. -7,5665) diubah jadi titik.
    """
    if name.lower().endswith(".csv"):
        df, last_error = None, None
        for enc in ("utf-8-sig", "latin-1"):
            try:
                df = pd.read_csv(io.BytesIO(data), sep=None, engine="python", encoding=enc)
                break
            except Exception as e:
                last_error = e
        if df is None:
            raise last_error
    else:
        df = pd.read_excel(io.BytesIO(data))

    rename = {
        c: str(c).strip().lower()
        for c in df.columns
        if str(c).strip().lower() in NORMALIZE_COLS and c != str(c).strip().lower()
    }
    if rename:
        df = df.rename(columns=rename)

    # File yang punya kolom `alamat` tapi belum punya kolom koordinat: sediakan kolom
    # kosong supaya baris-barisnya bisa dicari koordinatnya otomatis. (Tanpa `alamat`,
    # kolom koordinat yang hilang tetap dianggap error, supaya salah nama kolom —
    # mis. "lat"/"lng" — tidak diam-diam diperlakukan sebagai data tanpa koordinat.)
    if "merchant_name" in df.columns and "alamat" in df.columns:
        for col in ("latitude", "longitude"):
            if col not in df.columns:
                df[col] = np.nan

    for col in ("latitude", "longitude"):
        if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):  # pandas 3: teks bertipe "str", bukan object
            mask = df[col].notna()
            df.loc[mask, col] = df.loc[mask, col].astype(str).str.strip().str.replace(",", ".", regex=False)
    return df


# ---------- Geocoding otomatis (baris tanpa koordinat) ----------
GEO_SEP = "||"
GEO_MAX_PER_CLICK = 40     # batasi jumlah baris per klik supaya tidak menunggu terlalu lama
GEO_DELAY_SEC = 1.1        # kebijakan Nominatim: maksimal ~1 permintaan per detik


def _geo_key(name, alamat):
    return GEO_SEP.join(str(x if x is not None else "").strip().lower() for x in (name, alamat))


def geocode_candidates(name, alamat, city):
    """Daftar kueri pencarian untuk satu baris, dari yang paling spesifik."""
    name, alamat, city = (str(x if x is not None else "").strip() for x in (name, alamat, city))
    if name.lower() == "nan":
        name = ""
    if alamat.lower() == "nan":
        alamat = ""
    cands = []
    if alamat:
        cands.append(f"{alamat}, {city}" if city and city.lower() not in alamat.lower() else alamat)
    if name:
        cands.append(f"{name}, {city}" if city else name)
    if name and alamat:
        cands.append(f"{name}, {alamat}")
    seen, out = set(), []
    for c in cands:
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out


def geocode_place(name, alamat, city, search_fn=None, sleep_fn=None):
    """Cari koordinat satu merchant lewat Nominatim.

    Mengembalikan (hasil_atau_None, error_atau_None). `error` hanya diisi untuk
    kegagalan sementara (dibatasi/timeout/koneksi) — hasil kosong yang sah adalah
    (None, None), supaya kegagalan sementara tidak ikut tersimpan sebagai 'tidak ditemukan'.
    """
    search_fn = search_fn or search_nominatim
    sleep_fn = sleep_fn or time.sleep
    for i, query in enumerate(geocode_candidates(name, alamat, city)):
        if i > 0:
            sleep_fn(GEO_DELAY_SEC)
        results, err = search_fn(query, limit=1)
        if err:
            return None, err
        if results:
            top = results[0]
            try:
                return {
                    "lat": float(top["lat"]),
                    "lon": float(top["lon"]),
                    "label": str(top.get("display_name", ""))[:300],
                }, None
            except (KeyError, TypeError, ValueError):
                continue
    return None, None


def handle_missing_coordinates(df):
    """Isi koordinat baris yang kosong dari hasil pencarian otomatis (OpenStreetMap).

    Baris yang belum/tidak berhasil dicari tidak ikut dibuat rute — ditampilkan jelas
    supaya bisa dilengkapi manual. Mengembalikan DataFrame yang semua barisnya punya koordinat.
    """
    lat = pd.to_numeric(df["latitude"], errors="coerce")
    lon = pd.to_numeric(df["longitude"], errors="coerce")
    missing_mask = lat.isna() | lon.isna()
    if not missing_mask.any():
        return df

    df = df.copy()
    df["latitude"], df["longitude"] = lat, lon
    has_alamat = "alamat" in df.columns
    city = st.session_state.geocode_city.strip()
    cache = st.session_state.geocode_cache

    def key_of(i):
        return _geo_key(df.at[i, "merchant_name"], df.at[i, "alamat"] if has_alamat else "")

    flash = st.session_state.geocode_flash
    if flash:
        st.session_state.geocode_flash = None
        {"error": st.error, "warning": st.warning, "success": st.success}.get(flash[0], st.info)(flash[1])

    resolved, pending, failed = [], [], []
    for i in df.index[missing_mask]:
        entry = cache.get(key_of(i))
        if entry and "lat" in entry:
            df.at[i, "latitude"], df.at[i, "longitude"] = entry["lat"], entry["lon"]
            resolved.append(i)
        elif entry and entry.get("failed") and entry.get("city", "") == city:
            failed.append(i)
        else:
            pending.append(i)

    if pending or failed:
        st.warning(
            f"📍 **{len(pending) + len(failed)} dari {len(df)} baris belum punya koordinat.** "
            "Baris ini belum ikut dibuat rute. Cari otomatis lewat OpenStreetMap (dari nama"
            + (" dan kolom `alamat`" if has_alamat else "")
            + "), atau lengkapi sendiri di file."
        )
        st.text_input(
            "Kota/wilayah (opsional — bikin pencarian lebih akurat)",
            value=st.session_state.geocode_city,
            key=_wk("_geo_city_widget"),
            on_change=_sync_geo_city,
            placeholder="contoh: Surakarta",
        )
    if pending:
        todo = pending[:GEO_MAX_PER_CLICK]
        label = f"🔎 Cari {len(todo)} koordinat otomatis"
        if len(pending) > len(todo):
            label += f" (dari {len(pending)})"
        if st.button(label, type="primary", width="stretch", key="_geo_run",
                     help="Memakai OpenStreetMap (gratis). Dibatasi ±1 pencarian per detik, jadi butuh waktu sekitar "
                          f"{math.ceil(len(todo) * GEO_DELAY_SEC)} detik. Cakupan merchant kecil/UMKM terbatas."):
            progress = FancyLoader("Mencari koordinat otomatis", f"0 dari {len(todo)} merchant", pct=0.0)
            found_n, abort_msg, done_keys = 0, None, set()
            for n, i in enumerate(todo, start=1):
                k = key_of(i)
                if k in done_keys:
                    continue
                done_keys.add(k)
                res, err = geocode_place(
                    df.at[i, "merchant_name"], df.at[i, "alamat"] if has_alamat else "", city
                )
                if err:
                    abort_msg = err
                    break
                if res:
                    cache[k] = {**res, "city": city}
                    found_n += 1
                else:
                    cache[k] = {"failed": True, "city": city}
                progress.update(sub=f"{n} dari {len(todo)} merchant", pct=n / len(todo))
                time.sleep(GEO_DELAY_SEC)
            progress.close()
            if abort_msg:
                st.session_state.geocode_flash = (
                    "error", f"⚠️ Pencarian berhenti di tengah jalan: {abort_msg} Hasil yang sudah ketemu tetap tersimpan — klik lagi untuk melanjutkan."
                )
            else:
                st.session_state.geocode_flash = (
                    "success", f"✅ Selesai: {found_n} koordinat ditemukan dari {len(done_keys)} pencarian."
                )
            st.rerun()

    if resolved:
        df.loc[resolved, "koordinat_dari"] = "OpenStreetMap (otomatis)"
        df["koordinat_dari"] = df["koordinat_dari"].fillna("")
        with st.expander(f"📍 {len(resolved)} koordinat hasil pencarian otomatis — periksa dulu", expanded=False):
            st.caption(
                "OpenStreetMap kadang menebak tempat yang salah, terutama untuk nama umum. "
                "Cocokkan kolom **Hasil pencarian** dengan merchant yang kamu maksud."
            )
            check_df = pd.DataFrame({
                "merchant_name": df.loc[resolved, "merchant_name"].values,
                "Hasil pencarian": [cache.get(key_of(i), {}).get("label", "") for i in resolved],
                "latitude": df.loc[resolved, "latitude"].values,
                "longitude": df.loc[resolved, "longitude"].values,
            })
            st.dataframe(check_df, width="stretch", hide_index=True)
            export_cols = [c for c in df.columns if c not in ("source_file", "koordinat_dari", "route")]
            export_buf = io.BytesIO()
            with pd.ExcelWriter(export_buf, engine="openpyxl") as writer:
                df.loc[~df.index.isin(pending + failed), export_cols].to_excel(writer, index=False)
            st.download_button(
                "⬇️ Simpan data + koordinat (Excel)", data=export_buf.getvalue(),
                file_name="data_dengan_koordinat.xlsx", mime="application/vnd.ms-excel",
                help="Simpan supaya lain kali tidak perlu mencari koordinatnya lagi.",
                key="_geo_export",
            )

    if failed:
        with st.expander(f"❌ {len(failed)} baris tidak ketemu koordinatnya — perlu dilengkapi manual", expanded=True):
            st.dataframe(
                df.loc[failed, [c for c in ("merchant_name", "alamat") if c in df.columns]],
                width="stretch", hide_index=True,
            )
            st.caption(
                "Isi latitude/longitude-nya di file lalu upload ulang, atau tambahkan lewat **Maps Extractor** "
                "(link Google Maps, cari nama, atau input manual). Mengubah isian *Kota/wilayah* akan mencoba lagi."
            )

    left_out = pending + failed
    if left_out:
        df = df.drop(index=left_out)
    if df.empty:
        st.info("Belum ada baris dengan koordinat — cari koordinatnya dulu atau lengkapi di file.")
        st.stop()
    return df


# ---------- Pemeriksaan data janggal & pratinjau peta ----------
def _hav_km_matrix(lat, lon):
    """Matriks jarak garis lurus (km) antar semua titik, vektorisasi numpy."""
    la, lo = np.radians(np.asarray(lat, float)), np.radians(np.asarray(lon, float))
    dla, dlo = la[:, None] - la[None, :], lo[:, None] - lo[None, :]
    a = np.sin(dla / 2) ** 2 + np.cos(la)[:, None] * np.cos(la)[None, :] * np.sin(dlo / 2) ** 2
    return 6371.0 * 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def _hav_km_to_point(lat, lon, lat0, lon0):
    la, lo = np.radians(np.asarray(lat, float)), np.radians(np.asarray(lon, float))
    la0, lo0 = math.radians(lat0), math.radians(lon0)
    a = np.sin((la - la0) / 2) ** 2 + np.cos(la) * math.cos(la0) * np.sin((lo - lo0) / 2) ** 2
    return 6371.0 * 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def detect_outlier_points(df, min_points=5, floor_km=25.0, mad_k=6.0):
    """Titik yang jauh melenceng dari sebaran titik lainnya — biasanya salah koordinat
    (typo, lat/long tertukar, atau hasil pencarian otomatis yang salah tebak).

    Pendekatan robust: jarak tiap titik ke titik tengah (median) sebaran; dianggap janggal
    kalau jaraknya melebihi median + k×MAD dan juga di atas batas minimum `floor_km`
    (supaya sebaran yang rapat di satu kota tidak dikit-dikit ditandai).
    Mengembalikan {label_index: alasan}."""
    if len(df) < min_points:
        return {}
    lat = df["latitude"].to_numpy(float)
    lon = df["longitude"].to_numpy(float)
    med_lat, med_lon = float(np.median(lat)), float(np.median(lon))
    d = _hav_km_to_point(lat, lon, med_lat, med_lon)
    med = float(np.median(d))
    mad = float(np.median(np.abs(d - med))) * 1.4826
    thr = max(floor_km, med + mad_k * max(mad, 1.0))
    flagged = {}
    for pos in np.where(d > thr)[0]:
        reason = f"±{d[pos]:.0f} km dari pusat sebaran titik (umumnya ≤ {thr:.0f} km)"
        if -90 <= lon[pos] <= 90 and -180 <= lat[pos] <= 180:
            swapped = float(_hav_km_to_point([lon[pos]], [lat[pos]], med_lat, med_lon)[0])
            if swapped <= thr:
                reason += " — kemungkinan latitude & longitude tertukar"
        flagged[df.index[pos]] = reason
    return flagged


MAP_PREVIEW_MAX_POINTS = 1500

# ---------- Status merchant (pipeline akuisisi) ----------
STATUS_PROSPEK = "prospek"
STATUS_PENDEKATAN = "sedang pendekatan"
STATUS_AKUISISI = "sudah akuisisi"
STATUS_TIDAK = "belum tertarik"
STATUS_HILANG = "tidak ditemukan"      # hasil kunjungan "merchant tidak ditemukan": tidak dirutekan lagi
STATUS_OPTIONS = [STATUS_PROSPEK, STATUS_PENDEKATAN, STATUS_AKUISISI, STATUS_TIDAK, STATUS_HILANG]
# Merchant dengan status ini TIDAK dimasukkan ke rute (sudah dikuasai / tidak berminat / tidak ditemukan).
STATUS_EXCLUDED = (STATUS_AKUISISI, STATUS_TIDAK, STATUS_HILANG)
STATUS_COLORS = {
    STATUS_PROSPEK: "#2563EB", STATUS_PENDEKATAN: "#F59E0B",
    STATUS_AKUISISI: "#16A34A", STATUS_TIDAK: "#6B7280", STATUS_HILANG: "#B91C1C",
}
STATUS_EMOJI = {STATUS_PROSPEK: "🔵", STATUS_PENDEKATAN: "🟠", STATUS_AKUISISI: "🟢", STATUS_TIDAK: "⚪", STATUS_HILANG: "🔴"}


def normalize_status(v):
    """Samakan isian status dari Excel/CSV ke 4 nilai baku. Selain tiga status yang dikenali
    (dan kosong), hasilnya "prospek". Penolakan seperti "belum akuisisi" atau "sudah tertarik"
    tidak salah dibaca sebagai kebalikannya."""
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return STATUS_PROSPEK
    t = re.sub(r"\s+", " ", str(v).strip().lower())
    if not t or t in ("nan", "none"):
        return STATUS_PROSPEK
    if re.search(r"\b(tidak|tdk|belum)\b.*(ditemukan|ketemu)", t):
        return STATUS_HILANG
    if re.search(r"\b(belum|tidak|tdk|kurang)\b.*(tertarik|minat)", t) or "menolak" in t:
        return STATUS_TIDAK
    if re.search(r"\b(belum|bukan|tidak|tdk)\b.*(akuisisi|akusisi)", t):
        return STATUS_PROSPEK
    if "akuisisi" in t or "akusisi" in t:
        return STATUS_AKUISISI
    if re.search(r"\b(belum|tidak|tdk)\b.*pendekatan", t):
        return STATUS_PROSPEK
    if "pendekatan" in t:
        return STATUS_PENDEKATAN
    return STATUS_PROSPEK


def ensure_status_column(df):
    """Pastikan ada kolom `status` berisi nilai baku (default "prospek")."""
    df = df.copy()
    if "status" not in df.columns:
        df["status"] = STATUS_PROSPEK
    df["status"] = df["status"].apply(normalize_status)
    return df


def status_counts(df):
    counts = df["status"].value_counts() if "status" in df.columns else {}
    return {k: int(counts.get(k, 0)) for k in STATUS_OPTIONS}


def _pin_html(name, color, ring, show_label):
    dot = (
        f"<span style=\"width:14px;height:14px;border-radius:50%;background:{color};border:2px solid #fff;"
        f"box-shadow:0 0 0 1px rgba(0,0,0,.45){',' + ring if ring else ''};flex:none;\"></span>"
    )
    label = (
        "<span style=\"font:600 11px/1.2 sans-serif;color:#111827;background:rgba(255,255,255,.88);"
        f"padding:1px 4px;border-radius:4px;box-shadow:0 0 2px rgba(0,0,0,.35);\">{html_lib.escape(str(name))}</span>"
        if show_label else ""
    )
    return (
        "<div style=\"display:flex;align-items:center;gap:4px;white-space:nowrap;"
        f"transform:translate(-8px,-8px);\">{dot}{label}</div>"
    )


def fit_js(map_name, south, west, north, east, padding=40, max_zoom=16):
    """JS yang memastikan peta pas menampilkan SEMUA titik. Folium hanya menghitung zoom saat peta dibuat — kalau
    panel (expander) sedang tertutup, ukuran peta 0 dan zoom jadi salah. Skrip ini menunggu peta benar-benar
    tampil (ResizeObserver), lalu menjalankan fitBounds."""
    return f"""
(function() {{
  var m = {map_name};
  var b = L.latLngBounds([[{south}, {west}], [{north}, {east}]]);
  var el = m.getContainer(), done = false;
  function tryFit() {{
    if (el.clientWidth > 0 && el.clientHeight > 0) {{
      m.invalidateSize();
      m.fitBounds(b, {{padding: [{padding}, {padding}], maxZoom: {max_zoom}}});
      return true;
    }}
    return false;
  }}
  if (!tryFit() && typeof ResizeObserver !== "undefined") {{
    var ro = new ResizeObserver(function() {{
      if (!done && tryFit()) {{ done = true; ro.disconnect(); }}
    }});
    ro.observe(el);
  }}
}})();
"""


def build_preview_map(df, flagged, selected_idx=None, show_labels=True):
    """Peta semua titik. Warna titik = status merchant; titik janggal diberi cincin merah dan
    titik yang sedang dipilih cincin hitam. Nama merchant tampil di samping titik (opsional).
    Pakai Marker (bukan CircleMarker) supaya klik mengembalikan koordinat titik yang persis."""
    fmap = folium.Map(
        location=[float(df["latitude"].median()), float(df["longitude"].median())],
        zoom_start=11, control_scale=True,
    )
    special = [i for i in df.index if i in flagged or i == selected_idx]
    normal = [i for i in df.index if i not in flagged and i != selected_idx][:MAP_PREVIEW_MAX_POINTS]
    for idx in normal + special:
        row = df.loc[idx]
        status = row["status"] if "status" in df.columns else STATUS_PROSPEK
        bad = idx in flagged
        ring = "0 0 0 4px #DC2626" if bad else ("0 0 0 4px #111827" if idx == selected_idx else "")
        tip = f"{row['merchant_name']} · {status}" + (" ⚠️ janggal" if bad else "")
        folium.Marker(
            [float(row["latitude"]), float(row["longitude"])],
            icon=folium.DivIcon(
                html=_pin_html(row["merchant_name"], STATUS_COLORS.get(status, "#2563EB"), ring, show_labels),
                icon_size=(0, 0), icon_anchor=(0, 0), class_name="pin-icon",
            ),
            tooltip=html_lib.escape(tip),  # tooltip dirender sebagai HTML — nama dari file harus di-escape
        ).add_to(fmap)
    shown = df.loc[normal + special] if (normal or special) else df
    south, north = float(shown["latitude"].min()), float(shown["latitude"].max())
    west, east = float(shown["longitude"].min()), float(shown["longitude"].max())
    fmap.fit_bounds([[south, west], [north, east]], padding=(40, 40), max_zoom=16)
    # pengaman: fit ulang begitu peta benar-benar terlihat (mis. expander baru dibuka)
    fmap.get_root().script.add_child(folium.Element(fit_js(fmap.get_name(), south, west, north, east)))
    return fmap


def pick_clicked_index(df, clicked, tooltip=None, tol_deg=2e-4):
    """Cari baris yang diklik di peta dari koordinat klik (st_folium: last_object_clicked).
    Titik kembar di lokasi yang sama dibedakan lewat teks tooltip. Mengembalikan label index atau None."""
    try:
        lat0, lon0 = float(clicked["lat"]), float(clicked["lng"])
    except (TypeError, KeyError, ValueError):
        return None
    if df.empty:
        return None
    d = np.hypot(df["latitude"].to_numpy(float) - lat0, df["longitude"].to_numpy(float) - lon0)
    dmin = float(d.min())
    if dmin > tol_deg:
        return None
    cand = list(np.where(d <= dmin + 1e-7)[0])
    if len(cand) > 1 and tooltip:
        match = [p for p in cand if str(df.iloc[p]["merchant_name"]) in str(tooltip)]
        if match:
            cand = match
    return df.index[cand[0]]


# ---------- Jam buka/tutup: isi manual di tabel Data Awal ----------
HOURS_COLS = ("jam_buka", "jam_tutup")
PRO_ONLY_COLS = HOURS_COLS + ("prioritas", "petugas")   # kolom data yang hanya dipakai di Mode Pro


def count_merchants_with_hours(df):
    """Jumlah merchant yang punya jam_buka dan/atau jam_tutup yang valid (HH:MM)."""
    cols = [c for c in HOURS_COLS if c in df.columns]
    if not cols or len(df) == 0:
        return 0
    return int(df[cols].apply(lambda row: any(_parse_hhmm(v) is not None for v in row), axis=1).sum())


def pro_columns_with_data(df):
    """Kolom khusus Pro (prioritas, jam operasional, petugas) yang benar-benar ada isinya di data.
    Dipakai Mode Basic untuk memberi tahu bahwa kolom itu diabaikan. Return [(label, jumlah_baris)]."""
    out = []
    if df is None or len(df) == 0:
        return out
    if "prioritas" in df.columns:
        n = int(df["prioritas"].apply(is_truthy).sum())
        if n:
            out.append(("prioritas", n))
    hour_cols = [c for c in HOURS_COLS if c in df.columns]
    if hour_cols:
        n = int(df[hour_cols].apply(lambda row: any(_parse_hhmm(v) is not None for v in row), axis=1).sum())
        if n:
            out.append(("jam operasional", n))
    if "petugas" in df.columns:
        n = int(df["petugas"].apply(lambda v: str(v).strip().lower() not in ("", "nan", "none")).sum())
        if n:
            out.append(("petugas", n))
    return out


def normalize_hhmm_text(val):
    """'8:00' / '08.00' / '8:00:00' -> '08:00'; kosong -> ''; format tidak valid -> None."""
    s_ = "" if val is None else str(val).strip()
    if s_.lower() in ("", "nan", "none"):
        return ""
    m = re.fullmatch(r"(\d{1,2})[:.](\d{2})(?::\d{2})?", s_)
    if not m:
        return None
    h, mi = int(m.group(1)), int(m.group(2))
    if not (0 <= h <= 23 and 0 <= mi <= 59):
        return None
    return f"{h:02d}:{mi:02d}"


def normalize_priority_changes(changed):
    """Kotak centang ⭐ prioritas (True/False) → teks 'ya' / 'tidak' (sama seperti kolom di Excel/CSV)."""
    out = {}
    for key, cols in changed.items():
        new = dict(cols)
        if "prioritas" in new:
            new["prioritas"] = "ya" if is_truthy(new["prioritas"]) else "tidak"
        out[key] = new
    return out


def normalize_hours_changes(changed):
    """Rapikan perubahan kolom jam_buka/jam_tutup dari tabel. Return (perubahan_valid, daftar_salah);
    daftar_salah berisi (row_key, kolom, nilai) untuk isian yang bukan format jam — tidak disimpan."""
    ok, bad = {}, []
    for key, cols in changed.items():
        for col, val in cols.items():
            if col in HOURS_COLS:
                norm = normalize_hhmm_text(val)
                if norm is None:
                    bad.append((key, col, val))
                    continue
                val = norm
            ok.setdefault(key, {})[col] = val
    return ok, bad


# ---------- Edit data langsung di tabel ----------
EDITABLE_COLS = ("merchant_name", "latitude", "longitude", "status", "alamat", "prioritas", "jam_buka", "jam_tutup",
                 "petugas")


def apply_data_edits(df, edits):
    """Terapkan hapus-baris & ubah-sel yang tersimpan (berdasarkan `_row_key` yang stabil)."""
    deleted = set(edits.get("deleted", []))
    changed = edits.get("changed", {})
    if not deleted and not changed:
        return df
    df = df.copy()
    if deleted:
        df = df[~df["_row_key"].isin(deleted)]
    for key, cols in changed.items():
        mask = df["_row_key"] == key
        if not mask.any():
            continue
        for col, val in cols.items():
            if col not in EDITABLE_COLS:
                continue
            if col not in df.columns:
                df[col] = None
            df[col] = df[col].astype(object)
            df.loc[mask, col] = val
    return df.reset_index(drop=True)


EXPORT_HELPER_COLS = ("_row_key", "source_file", "koordinat_dari", "route")


def build_edited_data_excel(edited_full, geo_filled=None):
    """Excel berisi data setelah edit tabel diterapkan (baris yang dihapus sudah hilang, sel
    yang diubah sudah berisi nilai baru). Koordinat hasil pencarian otomatis ikut diisikan
    (lewat `geo_filled`: _row_key, latitude, longitude); baris yang koordinatnya belum ketemu
    tetap ada dengan koordinat kosong. Kolom bantu internal tidak ikut diekspor, jadi file
    ini bisa langsung diupload lagi sebagai data baru."""
    out = edited_full.copy()
    out["latitude"] = pd.to_numeric(out["latitude"], errors="coerce")
    out["longitude"] = pd.to_numeric(out["longitude"], errors="coerce")
    if geo_filled is not None and "_row_key" in out.columns:
        filled = geo_filled.drop_duplicates("_row_key").set_index("_row_key")
        miss = out["latitude"].isna() | out["longitude"].isna()
        if miss.any():
            out.loc[miss, "latitude"] = out.loc[miss, "_row_key"].map(filled["latitude"])
            out.loc[miss, "longitude"] = out.loc[miss, "_row_key"].map(filled["longitude"])
    out = out.drop(columns=[c for c in EXPORT_HELPER_COLS if c in out.columns])
    first = [c for c in ("merchant_name", "latitude", "longitude", "status") if c in out.columns]
    out = out[first + [c for c in out.columns if c not in first]]
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        out.to_excel(writer, index=False, sheet_name="Data")
    return buf.getvalue()


def _cell_changed(a, b):
    a_na = a is None or (isinstance(a, float) and math.isnan(a)) or str(a).strip() in ("", "nan", "None")
    b_na = b is None or (isinstance(b, float) and math.isnan(b)) or str(b).strip() in ("", "nan", "None")
    if a_na and b_na:
        return False
    if a_na != b_na:
        return True
    try:
        return abs(float(a) - float(b)) > 1e-9
    except (TypeError, ValueError):
        return str(a).strip() != str(b).strip()


def _py_value(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    if hasattr(v, "item"):
        v = v.item()
    return v if isinstance(v, (str, int, float, bool)) else str(v)


def diff_data_edits(original, edited, cols):
    """Bandingkan tabel sebelum/sesudah diedit. Mengembalikan (daftar_key_dihapus, {key: {kolom: nilai}})."""
    orig = original.set_index("_row_key")
    ed = edited.set_index("_row_key")
    deleted, changed = [], {}
    for key in ed.index:
        if key not in orig.index:
            continue
        if bool(ed.at[key, "hapus"]):
            deleted.append(key)
            continue
        for col in cols:
            if col in ed.columns and _cell_changed(orig.at[key, col], ed.at[key, col]):
                changed.setdefault(key, {})[col] = _py_value(ed.at[key, col])
    return deleted, changed


def clean_data_edits(raw):
    """Validasi edit dari file sesi (diperlakukan sebagai data, bukan kode)."""
    out = {"deleted": [], "changed": {}}
    if not isinstance(raw, dict):
        return out
    if isinstance(raw.get("deleted"), list):
        out["deleted"] = [k[:300] for k in raw["deleted"][:20000] if isinstance(k, str)]
    if isinstance(raw.get("changed"), dict):
        for key, cols in list(raw["changed"].items())[:20000]:
            if not isinstance(key, str) or not isinstance(cols, dict):
                continue
            clean = {}
            for col, val in cols.items():
                if col in EDITABLE_COLS and (val is None or isinstance(val, (str, int, float, bool))):
                    clean[col] = val[:300] if isinstance(val, str) else val
            if clean:
                out["changed"][key[:300]] = clean
    return out


# ---------- Seimbangkan beban waktu antar rute ----------
def _nn_tour_km(D, members, start=None):
    """Panjang rute tetangga-terdekat (km) melalui `members`; `start` = indeks titik awal di D."""
    if not members:
        return 0.0
    remaining = np.array(members, dtype=int)
    if start is None:
        cur, remaining = int(remaining[0]), remaining[1:]
    else:
        cur = int(start)
    total = 0.0
    while remaining.size:
        dists = D[cur, remaining]
        j = int(np.argmin(dists))
        total += float(dists[j])
        cur = int(remaining[j])
        remaining = np.delete(remaining, j)
    return total


def balance_by_time(df, labels, visit_minutes, start=None, max_points=None,
                    max_iter=300, speed_kmh=FALLBACK_SPEED_KMH):
    """Pindahkan titik antar rute supaya beban waktu (perjalanan + kunjungan) lebih merata.

    Beban tiap rute DIPERKIRAKAN dari rute tetangga-terdekat garis lurus ÷ kecepatan rata-rata —
    murah dihitung, dan cukup untuk membandingkan rute satu sama lain (rute final tetap dihitung
    dengan jarak jalan asli + TSP). Tiap langkah memindahkan satu titik dari rute terberat ke rute
    tetangga selama itu menurunkan beban terberat; berhenti kalau tak ada lagi yang membaik.
    Mengembalikan (label_baru, info_dict)."""
    lat = df["latitude"].to_numpy(float)
    lon = df["longitude"].to_numpy(float)
    n = len(lat)
    start_idx = None
    if start is not None:
        lat = np.append(lat, start[0])
        lon = np.append(lon, start[1])
        start_idx = n
    D = _hav_km_matrix(lat, lon)
    labs = np.array(labels).copy()
    groups = {g: [int(i) for i in np.where(labs == g)[0]] for g in np.unique(labs)}

    def load(members):
        if not members:
            return 0.0
        return _nn_tour_km(D, members, start_idx) / speed_kmh * 60 + len(members) * visit_minutes

    def centroid(members):
        return float(np.mean(lat[members])), float(np.mean(lon[members]))

    loads = {g: load(m) for g, m in groups.items()}
    before = dict(loads)
    for _ in range(max_iter):
        src = max(loads, key=loads.get)
        if len(groups[src]) <= 1:
            break
        cur_max = loads[src]
        c_src = centroid(groups[src])
        others = sorted(
            (g for g in groups if g != src),
            key=lambda g: float(_hav_km_to_point([centroid(groups[g])[0]], [centroid(groups[g])[1]], *c_src)[0]),
        )
        best = None
        for dst in others[:4]:
            if max_points is not None and len(groups[dst]) >= max_points:
                continue
            c_dst = centroid(groups[dst])
            cands = sorted(
                groups[src],
                key=lambda i: float(_hav_km_to_point([lat[i]], [lon[i]], *c_dst)[0]),
            )[:6]
            rest_max = max((loads[g] for g in groups if g not in (src, dst)), default=0.0)
            for p in cands:
                new_src = [i for i in groups[src] if i != p]
                ls, ld = load(new_src), load(groups[dst] + [p])
                new_max = max(ls, ld, rest_max)
                if new_max < cur_max - 1e-6:
                    key = (new_max, abs(ls - ld))
                    if best is None or key < best[0]:
                        best = (key, p, dst, ls, ld)
        if best is None:
            break
        _, p, dst, ls, ld = best
        groups[src].remove(p)
        groups[dst].append(p)
        loads[src], loads[dst] = ls, ld
        labs[p] = dst
    info = {
        "before_spread_min": max(before.values()) - min(before.values()),
        "after_spread_min": max(loads.values()) - min(loads.values()),
        "before_max_min": max(before.values()),
        "after_max_min": max(loads.values()),
    }
    return labs, info


def _clock(dt, base_date):
    """Format jam 'HH:MM'; kalau lewat tengah malam tambahkan '(+N hari)'."""
    days = (dt.date() - base_date).days
    text = dt.strftime("%H:%M")
    return text + (f" (+{days} hari)" if days > 0 else "")


def build_schedule_waits(duration_matrix, order, start_dt, visit_sec, first_is_start, round_trip, open_secs=None):
    """Jam tiba/selesai tiap titik sepanjang urutan kunjungan, dengan waktu tunggu.

    Titik awal (kalau ada) tidak dihitung durasi kunjungan. `open_secs` = {indeks_titik: detik sejak jam mulai
    rute}: kalau tiba sebelum merchant buka, petugas MENUNGGU sampai buka (jam tiba = jam buka).
    Mengembalikan (jam_tiba, jam_selesai, jam_kembali_atau_None, jam_selesai_rute, detik_tunggu_per_titik)."""
    open_secs = open_secs or {}
    arrivals, departs, waits = [], [], []
    t = start_dt
    for k, node in enumerate(order):
        if k > 0:
            t = departs[-1] + datetime.timedelta(seconds=duration_matrix[order[k - 1]][node])
        wait = 0.0
        if node in open_secs and not (k == 0 and first_is_start):
            opening = start_dt + datetime.timedelta(seconds=open_secs[node])
            if t < opening:
                wait = (opening - t).total_seconds()
                t = opening
        arrivals.append(t)
        waits.append(wait)
        stay = 0 if (k == 0 and first_is_start) else visit_sec
        departs.append(t + datetime.timedelta(seconds=stay))
    back = None
    if round_trip and len(order) > 1:
        back = departs[-1] + datetime.timedelta(seconds=duration_matrix[order[-1]][order[0]])
    return arrivals, departs, back, (back or departs[-1]), waits


def build_schedule(duration_matrix, order, start_dt, visit_sec, first_is_start, round_trip):
    """Versi tanpa waktu tunggu: (jam_tiba, jam_selesai, jam_kembali_atau_None, jam_selesai_rute)."""
    return build_schedule_waits(duration_matrix, order, start_dt, visit_sec, first_is_start, round_trip)[:4]


def build_whatsapp_text(r, map_links):
    """Teks siap kirim (format WhatsApp) untuk satu rute."""
    df = r["df"]
    total_sec = r["duration_sec"] + r.get("visit_sec", 0) + r.get("wait_sec", 0)
    lines = [
        f"*Rute {r['route_id'] + 1}* — {len(df)} titik · ~{r['distance_km']:.1f} km · ~{format_duration(total_sec)}"
    ]
    if r.get("tanggal"):
        lines.append(f"📅 {fmt_day_label(datetime.date.fromisoformat(r['tanggal']), short=False)}")
    if r.get("driver"):
        lines.append(f"🧑‍✈️ Petugas: {r['driver']}")
    if r.get("depot_name"):
        lines.append(f"🏭 Titik awal: {r['depot_name']}")
        if r.get("from_my_location"):
            lines.append("📍 Navigasi Google Maps dimulai dari lokasi Anda saat link dibuka")
    elif r.get("from_my_location"):
        lines.append("📍 Titik awal: lokasi Anda saat membuka Google Maps")
    if r.get("finish_label"):
        lines.append(f"🏁 Estimasi selesai ±{r['finish_label']}")
    lines.append("")
    for _, row in df.iterrows():
        eta = f" ({row['jam_tiba']})" if "jam_tiba" in df.columns else ""
        star = "⭐ " if row.get("prioritas_flag") else ""
        warn = f" {row['jadwal_status']}" if row.get("jadwal_status", "").startswith(("⚠️", "⏳")) else ""
        lines.append(f"{int(row['sequence'])}. {star}{row['merchant_name']}{eta}{warn}")
    if r.get("round_trip"):
        lines.append("↩️ Lalu kembali ke titik awal")
    lines.append("")
    if len(map_links) == 1:
        lines.append(f"🗺️ Google Maps: {map_links[0][2]}")
    else:
        for i, (_, _, url) in enumerate(map_links, start=1):
            lines.append(f"🗺️ Google Maps bagian {i}: {url}")
    return "\n".join(lines)


def build_stepwise_text(r):
    """Teks WhatsApp/salin untuk NAVIGASI TITIK DEMI TITIK: tiap merchant punya satu tautan navigasi sendiri
    (dari lokasi pengguna saat tautan dibuka), jadi tidak bergantung pada navigasi multi-titik Google Maps."""
    df = r["df"]
    first_is_start = bool(r.get("has_start"))
    stops = df.iloc[1:] if first_is_start else df
    total_sec = r["duration_sec"] + r.get("visit_sec", 0) + r.get("wait_sec", 0)
    lines = [f"*Rute {r['route_id'] + 1} · navigasi titik demi titik* — {len(stops)} titik · ~{r['distance_km']:.1f} km · ~{format_duration(total_sec)}"]
    if r.get("tanggal"):
        lines.append(f"📅 {fmt_day_label(datetime.date.fromisoformat(r['tanggal']), short=False)}")
    if r.get("driver"):
        lines.append(f"🧑‍✈️ Petugas: {r['driver']}")
    if first_is_start and r.get("depot_name"):
        lines.append(f"🏭 Titik awal: {r['depot_name']}")
    lines.append("Ketuk 🧭 di tiap titik, urut dari nomor 1. Navigasi dimulai dari lokasi Anda saat tautan dibuka.")
    lines.append("")
    for _, row in stops.iterrows():
        eta = f" ({row['jam_tiba']})" if "jam_tiba" in df.columns else ""
        star = "⭐ " if row.get("prioritas_flag") else ""
        warn = f" {row['jadwal_status']}" if row.get("jadwal_status", "").startswith(("⚠️", "⏳")) else ""
        lines.append(f"{int(row['sequence'])}. {star}{row['merchant_name']}{eta}{warn}")
        lines.append(f"🧭 {stop_nav_url(round(float(row['latitude']), 6), round(float(row['longitude']), 6))}")
        lines.append("")
    if r.get("round_trip"):
        lines.append("↩️ Lalu kembali ke titik awal")
    return "\n".join(lines).rstrip()


# ==========================================================================================
# HASIL RUTE: finalisasi, ubah urutan manual, peta gabungan, lembar PDF
# ==========================================================================================
def finalize_route(route_df, order, distance_matrix, duration_matrix, route_id,
                   start_dt, visit_sec, has_start, round_trip, base_date, open_secs=None):
    """Bangun tabel rute + jadwal + total jarak/waktu dari sebuah URUTAN.

    Dipakai saat rute pertama kali dibuat (urutan dari TSP) dan saat pengguna
    mengubah urutan secara manual — matriks jarak/waktu dipakai ulang, jadi
    tidak perlu memanggil OSRM lagi.
    """
    optimized_df = route_df.iloc[order].reset_index(drop=True)
    optimized_df["sequence"] = optimized_df.index + 1
    optimized_df["route_name"] = f"Rute {route_id + 1}"
    arrivals, departs, back_dt, finish_dt, waits = build_schedule_waits(
        duration_matrix, order, start_dt, visit_sec, has_start, round_trip, open_secs
    )
    optimized_df["jam_tiba"] = [_clock(t, base_date) for t in arrivals]
    if visit_sec:
        optimized_df["jam_selesai"] = [_clock(t, base_date) for t in departs]

    if "prioritas" in optimized_df.columns:
        optimized_df["prioritas_flag"] = optimized_df["prioritas"].apply(is_truthy)

    n_late = 0
    if "jam_buka" in optimized_df.columns or "jam_tutup" in optimized_df.columns:
        statuses = []
        for k, dt in enumerate(arrivals):
            is_start_row = k == 0 and has_start
            jb = optimized_df["jam_buka"].iloc[k] if "jam_buka" in optimized_df.columns else None
            jt = optimized_df["jam_tutup"].iloc[k] if "jam_tutup" in optimized_df.columns else None
            status = "" if is_start_row else check_time_window(dt, jb, jt)
            if status == "✅" and waits[k] >= 60:
                status = f"⏳ tunggu {round(waits[k] / 60)} mnt (buka {dt.strftime('%H:%M')})"
            if status.startswith("⚠️"):
                n_late += 1
            statuses.append(status)
        optimized_df["jadwal_status"] = statuses

    n_visits = len(order) - (1 if has_start else 0)
    return {
        "df": optimized_df,
        "distance_km": route_leg_sum(distance_matrix, order, round_trip) / 1000,
        "duration_sec": route_leg_sum(duration_matrix, order, round_trip),
        "visit_sec": visit_sec * n_visits,
        "wait_sec": float(sum(waits)),
        "finish_label": _clock(finish_dt, base_date),
        "back_label": _clock(back_dt, base_date) if back_dt else None,
        "n_outside_hours": n_late,
    }


def build_excel_bytes(route_summaries):
    """Driver/depot ditambahkan sebagai kolom di sini (saat export), bukan
    disimpan permanen di r['df'] — supaya nilainya selalu yang terbaru
    walau diubah user setelah rute pertama kali dibuat."""
    parts = []
    for r in route_summaries:
        d = r["df"].copy()
        if r.get("driver"):
            d["petugas"] = r["driver"]
        if r.get("depot_name"):
            d["titik_awal"] = r["depot_name"]
        if r.get("tanggal"):
            d["tanggal"] = r["tanggal"]
            d["hari"] = r.get("hari", "")
        parts.append(d)
    final_df = pd.concat(parts, ignore_index=True)

    summary_rows = []
    for r in route_summaries:
        naive_km = r.get("naive_distance_km", r["distance_km"])
        saved_km = naive_km - r["distance_km"]
        summary_rows.append({
            "rute": f"Rute {r['route_id'] + 1}",
            "tanggal": r.get("tanggal", ""),
            "hari": r.get("hari", ""),
            "petugas": r.get("driver", ""),
            "titik_awal": r.get("depot_name", ""),
            "jumlah_titik": len(r["df"]),
            "jarak_km": round(r["distance_km"], 2),
            "waktu_perjalanan_menit": round(r["duration_sec"] / 60),
            "jarak_urutan_file_km": round(naive_km, 2),
            "hemat_km": round(saved_km, 2),
            "hemat_persen": round(saved_km / naive_km * 100, 1) if naive_km > 0 else 0.0,
        })
    summary_df = pd.DataFrame(summary_rows)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        _mat = build_schedule_matrix(route_summaries)
        if _mat is not None:
            _mat.to_excel(writer, sheet_name="Jadwal")
        final_df.to_excel(writer, index=False, sheet_name="Semua Rute")
        for r, d in zip(route_summaries, parts):
            sheet_name = (f"Rute {r['route_id'] + 1}"
                          + (f" {fmt_day_label(datetime.date.fromisoformat(r['tanggal']))}" if r.get("tanggal") else ""))[:31]
            d.to_excel(writer, index=False, sheet_name=sheet_name)
        summary_df.to_excel(writer, index=False, sheet_name="Ringkasan")
    return buffer.getvalue()


def route_links_info(r, max_waypoints):
    """Link Google Maps + nomor urut titik untuk sebuah rute (termasuk kaki pulang bila pulang-pergi).

    from_my_location: tiap link tanpa origin (Google Maps memakai posisi petugas saat link dibuka). Kalau rute punya titik awal
    (has_start), titik itu hanya dipakai untuk menghitung rute: link berisi titik kunjungan saja, dan pada rute pulang-pergi
    titik awal menjadi tujuan akhir. Indeks link selalu merujuk ke baris `link_df` (baris 0 = titik awal bila has_start)."""
    df = r["df"]
    mine = bool(r.get("from_my_location"))
    has_start = bool(r.get("has_start"))
    if mine and has_start:
        round_ = bool(r.get("round_trip"))
        base = pd.concat([df.iloc[1:], df.iloc[[0]]], ignore_index=True) if round_ else df.iloc[1:]
        links = [(ia + 1, ib + 1, url) for ia, ib, url in generate_google_maps_links(base, max_waypoints, from_my_location=True)]
        link_df = pd.concat([df, df.iloc[[0]]], ignore_index=True) if round_ else df
        seq_nums = list(df["sequence"]) + ([df["sequence"].iloc[0]] if round_ else [])
        return links, seq_nums, link_df
    # Dari "Lokasi anda" tanpa titik awal: kaki pulang tidak bisa dibuatkan link (tujuan tak bisa berupa posisi pengguna).
    is_round = bool(r.get("round_trip")) and not mine
    link_df = pd.concat([df, df.iloc[[0]]], ignore_index=True) if is_round else df
    seq_nums = list(df["sequence"]) + ([df["sequence"].iloc[0]] if is_round else [])
    return generate_google_maps_links(link_df, max_waypoints, from_my_location=mine), seq_nums, link_df


MAPS_PART_EMOJIS = ["🟦", "🟩", "🟧", "🟪", "🟨", "🟥", "🟫", "⬛"]
MAPS_PART_TINTS = [
    "rgba(37,99,235,0.18)", "rgba(22,163,74,0.18)", "rgba(234,88,12,0.18)", "rgba(147,51,234,0.18)",
    "rgba(202,138,4,0.20)", "rgba(220,38,38,0.18)", "rgba(120,53,15,0.20)", "rgba(71,85,105,0.22)",
]
MAPS_SEAM_TINT = "rgba(128,128,128,0.30)"


def maps_part_labels(map_links, n_rows):
    """Penanda bagian link Google Maps untuk tiap baris tabel rute.

    Mengembalikan (label_per_baris, warna_per_baris). Baris yang menjadi titik sambungan antar
    bagian (tujuan bagian sebelumnya sekaligus titik awal bagian berikutnya) memuat DUA bagian,
    mis. "🟦 1/3 → 🟩 2/3", dan diberi warna abu-abu supaya sambungannya kelihatan."""
    total = len(map_links)
    parts_of_row = [[] for _ in range(n_rows)]
    for k, (ia, ib, _url) in enumerate(map_links, start=1):
        for i in range(ia, min(ib, n_rows - 1) + 1):
            parts_of_row[i].append(k)
    labels, tints = [], []
    for ps in parts_of_row:
        labels.append(" → ".join(
            f"{MAPS_PART_EMOJIS[(k - 1) % len(MAPS_PART_EMOJIS)]} {k}/{total}" for k in ps
        ))
        if len(ps) == 1:
            tints.append(MAPS_PART_TINTS[(ps[0] - 1) % len(MAPS_PART_TINTS)])
        else:
            tints.append(MAPS_SEAM_TINT if ps else "")
    return labels, tints


def _work_sig(ss):
    """Sidik jari data yang ikut tersimpan di file sesi (data Extractor + edit tabel)."""
    raw = json.dumps([ss.get("extracted_data") or [], ss.get("data_edits") or {}], sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def unsaved_work_items(ss):
    """Daftar kerja yang akan hilang kalau halaman di-refresh. File yang diupload tidak dihitung
    (masih ada di komputer pengguna). Data Extractor + edit tabel dianggap aman setelah sesi disimpan,
    hasil rute dianggap aman setelah Excel/PDF-nya diunduh."""
    items = []
    if ss.get("session_saved_sig") != _work_sig(ss):
        n_ext = len(ss.get("extracted_data") or [])
        edits = ss.get("data_edits") or {}
        n_edit = len(edits.get("deleted", [])) + sum(len(c) for c in edits.get("changed", {}).values())
        if n_ext:
            items.append(f"{n_ext} data dari Maps Extractor")
        if n_edit:
            items.append(f"{n_edit} edit tabel")
    res = ss.get("route_result")
    if res and not res.get("saved"):
        items.append("hasil rute")
    return items


def _mark_session_saved():
    st.session_state.session_saved_sig = _work_sig(st.session_state)


def _mark_routes_saved():
    res = st.session_state.get("route_result")
    if res:
        res["saved"] = True


def _leave_guard_js(active):
    """Pasang/lepas konfirmasi bawaan browser saat halaman akan di-refresh atau ditutup.
    Listener dipasang sekali; yang berubah hanya penanda __rpDirty."""
    body = (
        f"w.__rpDirty={'true' if active else 'false'};"
        "if(!w.__rpGuard){w.__rpGuard=true;"
        "w.addEventListener('beforeunload',function(e){if(w.__rpDirty){e.preventDefault();e.returnValue='';}});}"
    )
    try:
        import inspect
        if "unsafe_allow_javascript" in inspect.signature(st.html).parameters:
            st.html(f"<script>try{{var w=window;{body}}}catch(e){{}}</script>", unsafe_allow_javascript=True)
            return
    except Exception:
        pass
    try:
        import streamlit.components.v1 as components
        components.html(f"<script>try{{var w=window.parent;{body}}}catch(e){{}}</script>", height=0)
    except Exception:
        pass


def render_unsaved_notice(slot, is_pro):
    """Banner 'belum tersimpan' + penjaga refresh. Dipanggil di awal dan akhir skrip memakai slot yang sama,
    supaya hasil yang baru dibuat di run ini langsung ikut terhitung."""
    ss = st.session_state
    items = unsaved_work_items(ss)
    if not items:
        slot.empty()
        if ss.get("_guard_on"):
            with slot.container():
                _leave_guard_js(False)
            ss["_guard_on"] = False
        return
    tips = []
    if "hasil rute" in items:
        tips.append("unduh Excel" + (" / PDF" if is_pro else "") + " hasil rutenya")
    if any(i != "hasil rute" for i in items):
        tips.append("simpan lewat **💾 Simpan / Buka Sesi**" if is_pro
                    else "unduh Excel datanya atau pilih **Pro** untuk Simpan / Buka Sesi")
    with slot.container():
        st.warning(
            f"⚠️ **Belum tersimpan:** {', '.join(items)}. Kalau halaman di-refresh atau ditutup, semuanya hilang. "
            f"Sebelum itu, {' dan '.join(tips)}."
        )
        _leave_guard_js(True)
    ss["_guard_on"] = True


def _move_stop(route_id, action):
    """Callback tombol ubah-urutan: up / down / top / bottom / reset."""
    res = st.session_state.get("route_result")
    if not res:
        return
    r = next((x for x in res["route_summaries"] if x["route_id"] == route_id), None)
    if r is None:
        return
    order = list(r["order"])
    min_pos = 1 if r["has_start"] else 0  # titik awal (kalau ada) terkunci di urutan pertama
    if action == "reset":
        new_order = list(r["optimal_order"])
    else:
        node = st.session_state.get(f"mv_sel_{route_id}")
        if node not in order:
            return
        p = order.index(node)
        if p < min_pos:
            return
        if action == "up" and p > min_pos:
            order[p - 1], order[p] = order[p], order[p - 1]
        elif action == "down" and p < len(order) - 1:
            order[p + 1], order[p] = order[p], order[p + 1]
        elif action == "top":
            order.insert(min_pos, order.pop(p))
        elif action == "bottom":
            order.append(order.pop(p))
        new_order = order
    r.update(
        finalize_route(
            r["route_df"], new_order, r["distance_matrix"], r["duration_matrix"], route_id,
            r["start_dt"], r["visit_sec_each"], r["has_start"], r["round_trip"], r["base_date"],
            r.get("open_secs"),
        )
    )
    r["order"] = new_order
    r["manual"] = new_order != r["optimal_order"]
    res["excel_bytes"] = build_excel_bytes(res["route_summaries"])
    res["saved"] = False   # urutan berubah — Excel/PDF yang sudah diunduh tidak lagi sama


def _row_sig(name, lat, lon):
    try:
        return (str(name).strip(), round(float(lat), 5), round(float(lon), 5))
    except (TypeError, ValueError):
        return (str(name).strip(), None, None)


def _save_territories(assign):
    """Callback: simpan penugasan petugas (wilayah) tiap merchant ke data sebagai edit kolom `petugas`."""
    ss = st.session_state
    n = 0
    for key, name in assign.items():
        ss.data_edits["changed"].setdefault(key, {})["petugas"] = name
        n += 1
    ss.data_edit_nonce += 1
    ss.territory_flash = f"🔒 Wilayah {n} merchant disimpan ke kolom petugas."


def render_reorder_controls(r):
    """Pilih satu merchant lalu geser naik/turun — sederhana dan nyaman di HP."""
    rid = r["route_id"]
    order, route_df = r["order"], r["route_df"]
    min_pos = 1 if r["has_start"] else 0
    movable = order[min_pos:]
    if len(movable) < 2:
        st.caption("Rute ini hanya punya satu merchant, tidak ada yang perlu diurutkan ulang.")
        return
    key = f"mv_sel_{rid}"
    if st.session_state.get(key) not in movable:
        st.session_state.pop(key, None)
    st.selectbox(
        "Pilih merchant yang mau dipindah",
        movable,
        format_func=lambda n, _o=order, _d=route_df: f"{_o.index(n) + 1}. {_d.loc[n, 'merchant_name']}",
        key=key,
    )
    with st.container(key=f"mvrow_a_{rid}"):
        b1, b2 = st.columns(2)
        with b1:
            st.button("⬆️ Naik", key=f"mv_up_{rid}", on_click=_move_stop, args=(rid, "up"), width='stretch')
        with b2:
            st.button("⬇️ Turun", key=f"mv_down_{rid}", on_click=_move_stop, args=(rid, "down"), width='stretch')
    with st.container(key=f"mvrow_b_{rid}"):
        b3, b4 = st.columns(2)
        with b3:
            st.button("⏫ Ke awal", key=f"mv_top_{rid}", on_click=_move_stop, args=(rid, "top"), width='stretch')
        with b4:
            st.button("⏬ Ke akhir", key=f"mv_bottom_{rid}", on_click=_move_stop, args=(rid, "bottom"), width='stretch')
    st.button(
        "↩️ Kembalikan ke urutan optimal", key=f"mv_reset_{rid}", on_click=_move_stop,
        args=(rid, "reset"), disabled=not r.get("manual"), width='stretch',
    )
    if r.get("manual"):
        dk = r["distance_km"] - r["optimal_distance_km"]
        dm = (r["duration_sec"] - r["optimal_duration_sec"]) / 60
        st.caption(f"✏️ Urutan diubah manual: {dk:+.1f} km · {dm:+.0f} menit dibanding urutan optimal.")
    if r["has_start"]:
        st.caption("Titik awal selalu di urutan pertama dan tidak bisa dipindah.")


def _text_color_for(hex_color):
    """Hitam/putih mana yang lebih terbaca di atas warna latar ini."""
    h = hex_color.lstrip("#")
    rr, gg, bb = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lin = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in (rr, gg, bb)]
    lum = 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
    return "#1f2937" if lum > 0.40 else "#ffffff"


def numbered_icon(label, color, is_start=False):
    """Penanda bulat bernomor berwarna sesuai rute (S = titik awal)."""
    bg = "#111827" if is_start else color
    fg = "#ffffff" if is_start else _text_color_for(color)
    size = 28 if len(str(label)) >= 3 else 24
    html = (
        f'<div style="background:{bg};color:{fg};border:2px solid #fff;border-radius:50%;'
        f'width:{size}px;height:{size}px;line-height:{size - 4}px;text-align:center;'
        f'font:700 12px/{size - 4}px sans-serif;box-shadow:0 1px 5px rgba(0,0,0,.45);">{label}</div>'
    )
    return folium.DivIcon(html=html, icon_size=(size, size), icon_anchor=(size // 2, size // 2))


def build_combined_map(route_summaries):
    """Satu peta untuk semua rute: warna berbeda per rute, bisa dinyalakan/dimatikan."""
    lats = [v for r in route_summaries for v in r["df"]["latitude"]]
    lons = [v for r in route_summaries for v in r["df"]["longitude"]]
    fmap = folium.Map(
        location=[sum(lats) / len(lats), sum(lons) / len(lons)], zoom_start=11, control_scale=True
    )
    drawn_start_coords = set()  # dedup per KOORDINAT, bukan sekali untuk semua rute —
                                 # penting untuk multi-depot, karena titik awal bisa beda-beda per rute
    for r in route_summaries:
        rid = r["route_id"]
        df = r["df"]
        color = ROUTE_COLORS[rid % len(ROUTE_COLORS)]
        dot = (
            f'<span style="display:inline-block;width:12px;height:12px;border-radius:50%;'
            f'background:{color};margin-right:6px;vertical-align:middle;"></span>'
        )
        n_stops = len(df) - (1 if r.get("has_start") else 0)
        group = folium.FeatureGroup(
            name=f"{dot}Rute {rid + 1} · {n_stops} titik · {r['distance_km']:.1f} km", show=True
        )
        coords = [[row["latitude"], row["longitude"]] for _, row in df.iterrows()]
        line = coords + ([coords[0]] if r.get("round_trip") else [])
        folium.PolyLine(line, weight=4, color=color, opacity=0.85).add_to(group)
        for idx, row in df.iterrows():
            is_start = bool(r.get("has_start")) and idx == 0
            if is_start:
                coord_key = (round(row["latitude"], 6), round(row["longitude"], 6))
                if coord_key in drawn_start_coords:
                    continue  # titik awal persis sama sudah digambar — hindari tumpuk-tindih
                drawn_start_coords.add(coord_key)
            eta = row["jam_tiba"] if "jam_tiba" in df.columns else ""
            start_label = f"Titik awal · {row['merchant_name']}" if is_start else f"Rute {rid + 1} · {int(row['sequence'])}"
            tip = start_label if is_start else f"{start_label} · {row['merchant_name']}"
            folium.Marker(
                [row["latitude"], row["longitude"]],
                icon=numbered_icon("S" if is_start else int(row["sequence"]), color, is_start),
                tooltip=tip,
                popup=folium.Popup(f"{tip}" + (f"<br>Tiba ±{eta}" if eta else ""), max_width=260),
            ).add_to(group)
        group.add_to(fmap)
    folium.LayerControl(collapsed=False).add_to(fmap)
    fmap.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]], padding=(30, 30))
    return fmap


# --- PDF-START ---
try:
    from reportlab.lib import colors as rl_colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, KeepTogether, Flowable,
    )
    from reportlab.graphics.barcode.qr import QrCodeWidget
    from reportlab.graphics.shapes import Drawing

    PDF_OK = True
except Exception:  # reportlab belum terpasang -> fitur PDF disembunyikan, aplikasi tetap jalan
    PDF_OK = False

PDF_BRAND = "#2563EB"
_ID_MONTHS = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
              "Agustus", "September", "Oktober", "November", "Desember"]


def _pdf_safe(text):
    """Font bawaan PDF hanya mengenal Latin-1: samakan tanda baca umum, buang karakter yang tak didukung."""
    t = str(text if text is not None else "")
    for a, b in (("\u2013", "-"), ("\u2014", "-"), ("\u2018", "'"), ("\u2019", "'"),
                 ("\u201c", '"'), ("\u201d", '"'), ("\u00a0", " "), ("\u2022", "-")):
        t = t.replace(a, b)
    out = []
    for ch in t:
        try:
            ch.encode("latin-1")
            out.append(ch)
        except UnicodeEncodeError:
            plain = "".join(c for c in unicodedata.normalize("NFKD", ch) if not unicodedata.combining(c))
            try:
                plain.encode("latin-1")
                out.append(plain)
            except UnicodeEncodeError:
                pass  # emoji dsb. dibuang
    return "".join(out).strip()


def _fmt_date_id(iso):
    try:
        d = datetime.date.fromisoformat(iso)
        return f"{d.day} {_ID_MONTHS[d.month - 1]} {d.year}"
    except Exception:
        return ""


def _pdf_payload(r, links, seq_nums, result):
    """Ringkas satu rute jadi data polos (mudah di-cache) untuk dibuat PDF-nya."""
    df = r["df"]
    rows = []
    for _, row in df.iterrows():
        rows.append({
            "seq": int(row["sequence"]), "name": str(row["merchant_name"]),
            "lat": float(row["latitude"]), "lon": float(row["longitude"]),
            "tiba": str(row["jam_tiba"]) if "jam_tiba" in df.columns else "",
            "selesai": str(row["jam_selesai"]) if "jam_selesai" in df.columns else "",
            "priority": bool(row.get("prioritas_flag", False)),
            "note": str(row["jadwal_status"]) if row.get("jadwal_status") else "",
        })
    return {
        "route_no": int(r["route_id"]) + 1, "rows": rows,
        "has_start": bool(r.get("has_start")), "round_trip": bool(r.get("round_trip")),
        "from_my_location": bool(r.get("from_my_location")),
        "back_label": r.get("back_label") or "", "manual": bool(r.get("manual")),
        "distance_km": float(r["distance_km"]), "duration_sec": float(r["duration_sec"]),
        "visit_sec": float(r.get("visit_sec", 0)), "wait_sec": float(r.get("wait_sec", 0)),
        "finish_label": r.get("finish_label") or "",
        "show_selesai": "jam_selesai" in df.columns,
        "links": [(int(a), int(b), u) for a, b, u in links],
        "seq_nums": [int(x) for x in seq_nums],
        "date": r.get("tanggal") or ("" if r.get("petugas") else result.get("base_date", "")), "start_label": result.get("start_label", ""),
        "driver": r.get("driver") or "", "depot_name": r.get("depot_name") or "",
    }


if PDF_OK:
    class _SetRoute(Flowable):
        """Penanda tak terlihat: memberi tahu footer halaman ini milik rute yang mana."""
        def __init__(self, label):
            super().__init__()
            self.label = label
            self.width = self.height = 0

        def draw(self):
            self.canv._route_label = self.label

    class _CheckBox(Flowable):
        """Kotak kosong untuk dicentang petugas dengan pena."""
        def __init__(self, size=5.0 * mm):
            super().__init__()
            self.size = size
            self.width = self.height = size

        def draw(self):
            self.canv.setStrokeColor(rl_colors.HexColor("#6B7280"))
            self.canv.setLineWidth(1)
            self.canv.roundRect(0, 0, self.size, self.size, 1.2 * mm, stroke=1, fill=0)


def _qr_shorten(url):
    """Perpendek URL untuk QR supaya kodenya tidak terlalu padat (lebih mudah dipindai):
    koordinat dibulatkan ke 5 desimal (~1 m) dan travelmode dibuang (Maps default-nya mobil)."""
    url = url.replace("&travelmode=driving", "")
    return re.sub(r"-?\d+\.\d{6,}", lambda m: f"{float(m.group(0)):.5f}", url)


def _qr_drawing(url, size):
    widget = QrCodeWidget(_qr_shorten(url), barLevel="L")
    x0, y0, x1, y1 = widget.getBounds()
    w, h = x1 - x0, y1 - y0
    d = Drawing(size, size, transform=[size / w, 0, 0, size / h, 0, 0])
    d.add(widget)
    return d


def build_routes_pdf(payloads):
    """Satu PDF; tiap rute mulai di halaman baru. Untuk satu rute = lembar cetak per petugas."""
    buf = io.BytesIO()
    doc = BaseDocTemplate(
        buf, pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm,
        topMargin=14 * mm, bottomMargin=18 * mm,
        title="Lembar Rute", author="Routing & Extractor",
    )
    state = {"label": None, "page": 0}

    def footer(canvas, _doc):
        label = getattr(canvas, "_route_label", "")
        state["page"] = 1 if label != state["label"] else state["page"] + 1
        state["label"] = label
        canvas.saveState()
        canvas.setStrokeColor(rl_colors.HexColor("#D1D5DB"))
        canvas.line(14 * mm, 13 * mm, A4[0] - 14 * mm, 13 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(rl_colors.HexColor("#6B7280"))
        canvas.drawString(14 * mm, 8.5 * mm, f"{label}  -  Halaman {state['page']}")
        canvas.drawRightString(A4[0] - 14 * mm, 8.5 * mm, "Routing & Extractor")
        canvas.restoreState()

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPageEnd=footer)])

    st_title = ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=24, leading=28, textColor=rl_colors.white)
    st_kicker = ParagraphStyle("k", fontName="Helvetica", fontSize=8.5, leading=11, textColor=rl_colors.HexColor("#DBEAFE"))
    st_right = ParagraphStyle("r", fontName="Helvetica", fontSize=9.5, leading=13, textColor=rl_colors.white, alignment=2)
    st_meta = ParagraphStyle("m", fontName="Helvetica", fontSize=9.5, leading=14, textColor=rl_colors.HexColor("#111827"))
    st_cell = ParagraphStyle("c", fontName="Helvetica", fontSize=9.5, leading=12, textColor=rl_colors.HexColor("#111827"))
    st_head = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=rl_colors.white)
    st_small = ParagraphStyle("s", fontName="Helvetica", fontSize=8, leading=10, textColor=rl_colors.HexColor("#6B7280"))
    st_h2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=rl_colors.HexColor("#111827"))

    story = []
    for pi, p in enumerate(payloads):
        if pi > 0:
            story.append(PageBreak())
        label = f"Rute {p['route_no']}"
        story.append(_SetRoute(label))

        band = Table(
            [[[Paragraph("LEMBAR RUTE", st_kicker), Paragraph(label, st_title)],
              Paragraph(
                  xml_escape(_fmt_date_id(p["date"]))
                  + (f"<br/>Mulai {xml_escape(p['start_label'])}" if p["start_label"] else ""), st_right)]],
            colWidths=[doc.width * 0.62, doc.width * 0.38],
        )
        band.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), rl_colors.HexColor(PDF_BRAND)),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))
        story += [band, Spacer(1, 4 * mm)]

        n_stops = len(p["rows"]) - (1 if p["has_start"] else 0)
        parts = [f"<b>{n_stops}</b> merchant", f"<b>~{p['distance_km']:.1f} km</b>",
                 f"Perjalanan {xml_escape(format_duration(p['duration_sec']))}"]
        if p["visit_sec"]:
            parts.append(f"Kunjungan {xml_escape(format_duration(p['visit_sec']))}")
        if p.get("wait_sec", 0) >= 60:
            parts.append(f"Menunggu toko buka {xml_escape(format_duration(p['wait_sec']))}")
        if p["finish_label"]:
            parts.append(f"Selesai +/-{xml_escape(p['finish_label'])}" + (" (sudah pulang)" if p["round_trip"] else ""))
        if p.get("depot_name"):
            parts.append(f"Titik awal: {xml_escape(p['depot_name'])}" + (" (navigasi dari lokasi pengguna)" if p.get("from_my_location") else ""))
        elif p.get("from_my_location"):
            parts.append("Titik awal: lokasi pengguna saat membuka Google Maps")
        story.append(Paragraph("  |  ".join(parts), st_meta))
        story.append(Spacer(1, 2 * mm))
        petugas_val = f"<b>{xml_escape(p['driver'])}</b>" if p.get("driver") else "________________________________"
        story.append(Paragraph(
            f"Petugas: {petugas_val} &nbsp;&nbsp;&nbsp; Kendaraan / Plat: ____________________", st_meta))
        if p["manual"]:
            story.append(Spacer(1, 1.5 * mm))
            story.append(Paragraph("Urutan kunjungan telah disesuaikan secara manual.", st_small))
        story.append(Spacer(1, 4 * mm))

        # tabel kunjungan
        head = ["No", "Merchant", "Tiba"] + (["Selesai"] if p["show_selesai"] else []) + ["Cek", "Catatan"]
        data = [[Paragraph(h, st_head) for h in head]]

        def row_cells(no, name_html, tiba, selesai, note=""):
            cells = [Paragraph(no, st_cell), Paragraph(name_html, st_cell), Paragraph(xml_escape(tiba), st_cell)]
            if p["show_selesai"]:
                cells.append(Paragraph(xml_escape(selesai), st_cell))
            note_color = "#DC2626" if note.startswith("⚠️") else "#111827"
            cells += [_CheckBox(), Paragraph(f"<font color='{note_color}'>{xml_escape(_pdf_safe(note))}</font>", st_cell)]
            return cells

        for i, row in enumerate(p["rows"]):
            is_start = p["has_start"] and i == 0
            name = xml_escape(_pdf_safe(row["name"])) or "-"
            # "⭐" bukan karakter Latin-1 dan akan hilang diam-diam di font PDF
            # bawaan, jadi dipakai label teks biasa supaya tetap kelihatan di cetakan.
            star = "<font color='#D97706'><b>[PRIORITAS]</b></font> " if row.get("priority") and not is_start else ""
            prefix = "<font color='#2563EB'><b>[TITIK AWAL]</b></font> " if is_start else star
            coord = f"<br/><font size='7' color='#6B7280'>{row['lat']:.6f}, {row['lon']:.6f}</font>"
            data.append(row_cells("S" if is_start else str(row["seq"]), f"{prefix}<b>{name}</b>{coord}",
                                  row["tiba"], row["selesai"], row.get("note", "")))
        if p["round_trip"] and p["rows"]:
            data.append(row_cells("-", "<i>Kembali ke titik awal</i>", p["back_label"], ""))

        fixed = 11 + 20 + (20 if p["show_selesai"] else 0) + 12
        merch_w = 70
        notes_w = max(30, doc.width / mm - fixed - merch_w)
        widths = [11 * mm, merch_w * mm, 20 * mm] + ([20 * mm] if p["show_selesai"] else []) + [12 * mm, notes_w * mm]
        tbl = Table(data, colWidths=widths, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), rl_colors.HexColor("#1E3A8A")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [rl_colors.white, rl_colors.HexColor("#F3F6FC")]),
            ("GRID", (0, 0), (-1, -1), 0.5, rl_colors.HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (-2, 1), (-2, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(tbl)

        # QR Google Maps: 50 mm (cukup besar untuk dipindai kamera HP), maks. 3 per baris, maks. 6 bagian
        if p["links"]:
            story.append(Spacer(1, 6 * mm))
            total = len(p["links"])
            qr_cells = []
            for i, (ia, ib, url) in enumerate(p["links"][:6], start=1):
                cap = ("Buka seluruh rute di Google Maps" if total == 1
                       else f"Bagian {i}/{total}: titik {p['seq_nums'][ia]} - {p['seq_nums'][ib]}")
                qr_cells.append([_qr_drawing(url, 50 * mm), Paragraph(xml_escape(cap), st_small)])
            qr_rows = [qr_cells[k:k + 3] for k in range(0, len(qr_cells), 3)]
            qr_tbl = Table(qr_rows, colWidths=[58 * mm] * min(3, len(qr_cells)), hAlign="LEFT")
            qr_tbl.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
            block = [Paragraph("Scan dengan kamera HP untuk membuka rute di Google Maps", st_h2),
                     Spacer(1, 2 * mm), qr_tbl]
            if total > 6:
                block.append(Paragraph(f"Rute panjang dibagi {total} bagian; 6 bagian pertama ditampilkan.", st_small))
            story.append(KeepTogether(block))

    doc.build(story)
    return buf.getvalue()


@st.cache_data(show_spinner=False, max_entries=64)
def _routes_pdf_cached(payloads):
    return build_routes_pdf(payloads)
# --- PDF-END ---


def _template_df():
    return pd.DataFrame(
        {
            "merchant_name": ["Toko A", "Toko B", "Toko C"],
            "latitude": [-7.5665, -7.5700, -7.5610],
            "longitude": [110.8167, 110.8200, 110.8100],
        }
    )


def make_template_excel():
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        _template_df().to_excel(writer, index=False)
    return buf.getvalue()


def make_template_csv():
    return _template_df().to_csv(index=False).encode("utf-8-sig")


# ==========================================================================================
# SESSION STATE INIT
# ==========================================================================================
if "page" not in st.session_state:
    st.session_state.page = "Routing"
if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = []
if "routing_df" not in st.session_state:
    st.session_state.routing_df = None
# Streamlit membuang state widget yang tidak dirender (mis. saat pindah halaman).
# Karena itu input halaman Routing disimpan di session_state biasa, bukan di widget.
if "uploaded_store" not in st.session_state:
    st.session_state.uploaded_store = {}  # {nama_file: bytes}
if "uploader_nonce" not in st.session_state:
    st.session_state.uploader_nonce = 0  # ganti key uploader supaya kosong setelah file disimpan
if "use_extracted_flag" not in st.session_state:
    st.session_state.use_extracted_flag = False
if "nearest_on_flag" not in st.session_state:
    st.session_state.nearest_on_flag = False      # hanya ambil N merchant terdekat dari titik awal
if "nearest_n_flag" not in st.session_state:
    st.session_state.nearest_n_flag = 20
if "starting_link_saved" not in st.session_state:
    st.session_state.starting_link_saved = ""
if "sheet_link_saved" not in st.session_state:
    st.session_state.sheet_link_saved = ""     # link Google Sheet terakhir yang berhasil diambil (ikut tersimpan di sesi)
if "start_mode_saved" not in st.session_state:
    st.session_state.start_mode_saved = "mylocation"   # kotak "navigasi dari lokasi petugas": "mylocation" = tercentang (bawaan), "manual" = tidak
if "multi_depot_rows" not in st.session_state:
    st.session_state.multi_depot_rows = []  # id unik per baris, misal [1, 2, 3]
if "multi_depot_next_id" not in st.session_state:
    st.session_state.multi_depot_next_id = 1
if "use_multi_depot_flag" not in st.session_state:
    st.session_state.use_multi_depot_flag = False
if "row_key_map" not in st.session_state:
    st.session_state.row_key_map = {}         # {(nama, lat, lon): row_key} — mencocokkan baris hasil rute ke data
if "territory_flash" not in st.session_state:
    st.session_state.territory_flash = None
if "driver_names" not in st.session_state:
    st.session_state.driver_names = {}  # {route_id: nama}
if "geocode_cache" not in st.session_state:
    st.session_state.geocode_cache = {}  # {"nama||alamat": {lat, lon, label, city} | {failed, city}}
if "geocode_city" not in st.session_state:
    st.session_state.geocode_city = ""
if "geocode_flash" not in st.session_state:
    st.session_state.geocode_flash = None  # (jenis, pesan) ditampilkan sekali di run berikutnya
if "data_edits" not in st.session_state:
    st.session_state.data_edits = {"deleted": [], "changed": {}}  # edit tabel Data Awal, per _row_key
if "data_edit_nonce" not in st.session_state:
    st.session_state.data_edit_nonce = 0
if "map_selected_key" not in st.session_state:
    st.session_state.map_selected_key = None   # _row_key merchant yang dipilih di pratinjau peta
if "map_last_click_sig" not in st.session_state:
    st.session_state.map_last_click_sig = None
if "map_panel_open" not in st.session_state:
    st.session_state.map_panel_open = False
if "table_panel_open" not in st.session_state:
    st.session_state.table_panel_open = False
if "exclude_outliers_flag" not in st.session_state:
    st.session_state.exclude_outliers_flag = False
if "balance_time_flag" not in st.session_state:
    st.session_state.balance_time_flag = False
if "hours_opt_flag" not in st.session_state:
    st.session_state.hours_opt_flag = True
if "presets" not in st.session_state:
    st.session_state.presets = {}  # {nama_preset: {pengaturan}} — khusus Mode Pro
if "preset_flash" not in st.session_state:
    st.session_state.preset_flash = None
if "widget_nonce" not in st.session_state:
    st.session_state.widget_nonce = 0
if "preset_panel_open" not in st.session_state:
    st.session_state.preset_panel_open = False   # tetap terbuka setelah pengguna memilih/menerapkan preset


def _wk(name):
    """Kunci widget pengaturan, ditambah nomor versi. Nomor naik saat preset diterapkan atau sesi dibuka.
    Kunci baru = widget baru di browser yang langsung memakai nilai terbaru. Cukup menghapus kunci lama di server
    tidak memadai: Streamlit mengenali widget dari kuncinya, jadi browser tetap menampilkan nilai lamanya."""
    return f"{name}__{st.session_state.widget_nonce}"


def _detect_default_mode():
    """Tebak mode awal dari User-Agent: HP -> Mobile, selain itu Desktop."""
    try:
        ua = (st.context.headers.get("User-Agent") or "").lower()
    except Exception:
        return "Desktop"
    return "Mobile" if ("iphone" in ua or "ipod" in ua or "mobile" in ua) else "Desktop"


if "view_mode" not in st.session_state:
    st.session_state.view_mode = _detect_default_mode()
IS_MOBILE = st.session_state.view_mode == "Mobile"

if "app_mode" not in st.session_state:
    st.session_state.app_mode = "Basic"  # pengguna baru mulai dari tampilan yang paling ringkas
IS_PRO = st.session_state.app_mode == "Pro"

MOBILE_CSS = """
<style>
/* ===== MODE HANDPHONE ===== */
.block-container {padding: 3.4rem 0.8rem 4rem 0.8rem !important; max-width: 100% !important;}
section[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {display: none !important;}

.hero-header {padding: 16px 16px; border-radius: 14px; margin-bottom: 14px;}
.hero-header h1 {font-size: 1.25rem;}
.hero-header p {font-size: 0.8rem; line-height: 1.4;}
.hero-art {display: none;}
.stat-strip {grid-template-columns: repeat(2, minmax(0, 1fr));}
.stat {padding: 16px 16px 14px 16px;}
.stat:nth-child(3) {border-left: 0;}
.stat:nth-child(n+3) {border-top: 1px solid rgba(128,128,128,0.2);}
.cmp {flex-direction: column; align-items: stretch; gap: 18px; padding: 18px;}
.cmp-row {grid-template-columns: 1fr auto;}
.cmp-track {grid-column: 1 / -1; order: 3;}
.cmp-save {padding-left: 0; border-left: 0; padding-top: 16px; border-top: 1px solid rgba(128,128,128,0.2);}
.section-header {margin: 20px 0 10px 0; gap: 10px;}
.section-header .badge {width: 32px; height: 32px;}
.metric-card {padding: 12px 14px;}
.metric-card .metric-value {font-size: 1.25rem;}
.empty-state {padding: 26px 16px;}

/* target sentuh lebih besar + cegah zoom otomatis iOS */
.stButton > button, .stDownloadButton > button, .stLinkButton > a {
    min-height: 3rem; font-size: 1rem !important;
}
input, textarea, [data-baseweb="select"] {font-size: 16px !important;}
[data-testid="stFileUploaderDropzone"] {padding: 1rem;}

/* semua kolom ditumpuk ke bawah */
[data-testid="stHorizontalBlock"] {flex-direction: column !important; gap: 0.6rem !important;}
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
[data-testid="stHorizontalBlock"] > [data-testid="column"] {
    width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important;
}

/* pengecualian: baris yang tetap berdampingan */
.st-key-navrow [data-testid="stHorizontalBlock"],
.st-key-moderow [data-testid="stHorizontalBlock"],
.st-key-userrow [data-testid="stHorizontalBlock"],
[class*="st-key-mvrow"] [data-testid="stHorizontalBlock"],
[class*="st-key-filerow"] [data-testid="stHorizontalBlock"] {
    flex-direction: row !important; flex-wrap: nowrap !important; gap: 0.5rem !important;
}
.st-key-navrow [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
.st-key-moderow [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
.st-key-userrow [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
[class*="st-key-mvrow"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
.st-key-navrow [data-testid="stHorizontalBlock"] > [data-testid="column"],
.st-key-moderow [data-testid="stHorizontalBlock"] > [data-testid="column"],
.st-key-userrow [data-testid="stHorizontalBlock"] > [data-testid="column"],
[class*="st-key-mvrow"] [data-testid="stHorizontalBlock"] > [data-testid="column"] {
    width: auto !important; flex: 1 1 0 !important; min-width: 0 !important;
}
.st-key-moderow .stButton > button {min-height: 2.4rem; font-size: 0.85rem !important;}
.st-key-userrow [data-testid="stColumn"]:last-child,
.st-key-userrow [data-testid="column"]:last-child {
    flex: 0 0 8rem !important; width: 8rem !important; min-width: 8rem !important;
}
.st-key-userrow .stButton > button {min-height: 2.4rem; font-size: 0.85rem !important;}
[class*="st-key-filerow"] [data-testid="stColumn"]:first-child,
[class*="st-key-filerow"] [data-testid="column"]:first-child {
    width: auto !important; flex: 1 1 0 !important; min-width: 0 !important; overflow-wrap: anywhere;
}
[class*="st-key-filerow"] [data-testid="stColumn"]:last-child,
[class*="st-key-filerow"] [data-testid="column"]:last-child {
    width: 3.2rem !important; flex: 0 0 3.2rem !important; min-width: 3.2rem !important;
}

/* kartu metrik: 2 kolom (grid) */
.st-key-grid2 [data-testid="stHorizontalBlock"],
.st-key-grid4 [data-testid="stHorizontalBlock"] {
    flex-direction: row !important; flex-wrap: wrap !important; gap: 0.6rem !important;
}
.st-key-grid2 [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
.st-key-grid4 [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
.st-key-grid2 [data-testid="stHorizontalBlock"] > [data-testid="column"],
.st-key-grid4 [data-testid="stHorizontalBlock"] > [data-testid="column"] {
    width: calc(50% - 0.3rem) !important; flex: 0 0 calc(50% - 0.3rem) !important;
    min-width: calc(50% - 0.3rem) !important;
}

/* ruang bawah aman untuk HP dengan bilah gestur / notch */
.block-container {padding-bottom: calc(4rem + env(safe-area-inset-bottom, 0px)) !important;}

/* Mode Lapangan: tombol aksi tetap berdampingan, besar, mudah ditekan satu jempol */
[class*="st-key-fmrow"] [data-testid="stHorizontalBlock"] {
    flex-direction: row !important; flex-wrap: nowrap !important; gap: 0.5rem !important;
}
[class*="st-key-fmrow"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
[class*="st-key-fmrow"] [data-testid="stHorizontalBlock"] > [data-testid="column"] {
    width: auto !important; flex: 1 1 0 !important; min-width: 0 !important;
}
[class*="st-key-fmrow_main"] .stButton > button {min-height: 3.8rem; font-size: 1.15rem !important; font-weight: 700;}
[class*="st-key-fmrow_aux"] .stButton > button {min-height: 2.6rem; font-size: 0.85rem !important;}
[class*="st-key-fm_nav"] .stLinkButton > a {min-height: 3.9rem; font-size: 1.2rem !important; font-weight: 700;}

/* pilihan tampilan hasil: satu baris yang bisa digeser (tidak patah ke dua baris) */
.st-key-resultview [role="radiogroup"] {flex-wrap: nowrap !important; overflow-x: auto; gap: 0.5rem 0.9rem !important; padding-bottom: 4px;}
.st-key-resultview [role="radiogroup"] label {white-space: nowrap;}

.stTabs [role="tablist"] {overflow-x: auto;}
.stTabs [data-baseweb="tab"] {padding: 0.5rem 0.7rem;}
div[data-testid="stExpander"] {margin-bottom: 10px; border-radius: 12px !important;}
</style>
"""
if IS_MOBILE:
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)

MAP_H = 260 if IS_MOBILE else 350
COMBINED_MAP_H = 380 if IS_MOBILE else 520
# Hanya kirim `height` di mode Mobile; height=None ditolak Streamlit versi baru.
TABLE_KW = {"height": 260} if IS_MOBILE else {}


# ================================================================
# LOGIN — halaman masuk sebelum menu app bisa dipakai
# ================================================================
# Kredensial TIDAK ada di kode. Atur lewat Secrets / env: APP_USERNAME dan APP_PASSWORD_HASH (disarankan; buat dengan
# buat_hash_password.py) atau APP_PASSWORD (teks biasa). Bila belum diatur, semua login ditolak (aman secara bawaan).
LOGIN_MAX_FAILS = 5        # gagal berturut-turut sebelum dikunci
LOGIN_LOCK_SECONDS = 60    # lama kunci
LOGIN_FAIL_WINDOW = 300    # kegagalan lama (detik) dianggap kedaluwarsa


HASH_PREFIX = "pbkdf2_sha256"


def hash_password(password, iterations=240_000, salt=None):
    """Format: pbkdf2_sha256$iterasi$salt(hex)$hash(hex). Sama dengan yang dibuat buat_hash_password.py."""
    salt = salt if salt is not None else os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"{HASH_PREFIX}${iterations}${salt.hex()}${dk.hex()}"


def verify_password(password, stored):
    """Cocokkan password dengan hash tersimpan (atau teks biasa bila stored bukan hash)."""
    if stored.startswith(HASH_PREFIX + "$"):
        try:
            _, it, salt_hex, hash_hex = stored.split("$")
            dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(it))
            return hmac.compare_digest(dk.hex(), hash_hex.lower())
        except Exception:
            return False
    return _same(password, stored)


def _auth_credentials():
    """(username, password_atau_hash) dari Secrets/env; None bila belum diatur."""
    user = _setting("APP_USERNAME")
    secret = _setting("APP_PASSWORD_HASH") or _setting("APP_PASSWORD")
    if not user or not secret:
        return None
    return str(user).strip(), str(secret).strip()


AUTH_COOKIE = "rp_auth"          # hanya untuk MENGHAPUS cookie login versi lama
AUTH_PARAM = "rpa"               # token login di URL: ikut terbawa saat refresh, hilang saat tab ditutup
AUTH_IDLE_SECONDS = 30 * 60      # keluar otomatis bila tidak dipakai selama ini


@st.cache_resource
def _auth_store():
    """Sesi login di memori server (bersama antar-rerun). Kunci = hash token; nilai = (user, terakhir dipakai)."""
    return {"lock": threading.Lock(), "tokens": {}}


def _tok_key(token):
    return hashlib.sha256(str(token).encode("utf-8")).hexdigest()


def auth_session_create(user, now, store=None):
    store = store or _auth_store()
    token = pysecrets.token_urlsafe(32)
    with store["lock"]:
        for k in [k for k, (_, seen) in store["tokens"].items() if now - seen > AUTH_IDLE_SECONDS]:
            del store["tokens"][k]               # bersihkan yang sudah kedaluwarsa
        store["tokens"][_tok_key(token)] = (user, now)
    return token


def auth_session_check(token, now, store=None, idle=AUTH_IDLE_SECONDS):
    """Return username bila token sah & tidak menganggur > idle detik (sekaligus menyegarkan waktu pakai); selain itu None."""
    if not isinstance(token, str) or not token:
        return None
    store = store or _auth_store()
    k = _tok_key(token)
    with store["lock"]:
        rec = store["tokens"].get(k)
        if not rec:
            return None
        user, seen = rec
        if now - seen > idle:
            del store["tokens"][k]
            return None
        store["tokens"][k] = (user, now)
        return user


AUTH_WARN_SECONDS = 120          # peringatan "masih menggunakan halaman?" muncul sebanyak ini sebelum login berakhir


def auth_session_remaining(token, now, store=None, idle=AUTH_IDLE_SECONDS):
    """Sisa detik sebelum login berakhir karena menganggur, TANPA menyegarkan waktu pakai. None bila token tidak ada."""
    if not isinstance(token, str) or not token:
        return None
    store = store or _auth_store()
    with store["lock"]:
        rec = store["tokens"].get(_tok_key(token))
        return None if not rec else idle - (now - rec[1])


def auth_touch(ss):
    """Tandai pengguna masih aktif (dipanggil dari bagian halaman yang interaktif tapi tidak menjalankan ulang seluruh skrip)."""
    tok = ss.get("auth_token")
    if ss.get("auth_ok") and tok:
        auth_session_check(tok, time.time())


def auth_session_end(token, store=None):
    store = store or _auth_store()
    with store["lock"]:
        store["tokens"].pop(_tok_key(token), None)


def _auth_set_url(token):
    try:
        if token is None:
            st.query_params.pop(AUTH_PARAM, None)
        elif st.query_params.get(AUTH_PARAM) != token:
            st.query_params[AUTH_PARAM] = token
    except Exception:
        pass


def auth_refresh():
    """Dipanggil di awal tiap run: pulihkan login dari token di URL (refresh) dan akhiri login yang menganggur > 30 menit."""
    ss = st.session_state
    now = time.time()
    if ss.get("auth_ok"):
        tok = ss.get("auth_token")
        user = auth_session_check(tok, now) if tok else None
        if user:
            _auth_set_url(tok)
            return
        ss["auth_ok"] = False                    # kedaluwarsa (atau server dimulai ulang): minta login lagi
        ss.pop("auth_token", None)
        ss["login_flash"] = "Sesi berakhir karena tidak digunakan lebih dari 30 menit. Silakan masuk lagi."
        ss["auth_expired"] = True                # data sesi tetap di memori & Supabase; hanya layar login yang tampil
        _auth_set_url(None)
        return
    if ss.get("no_autologin"):
        return
    try:
        tok = st.query_params.get(AUTH_PARAM)
    except Exception:
        return
    user = auth_session_check(tok, now)
    if user:
        ss["auth_ok"], ss["auth_user"], ss["auth_token"] = True, user, tok
    elif tok:
        _auth_set_url(None)                      # token basi di URL: buang


def _same(a, b):
    """Bandingkan string tanpa bocor waktu (constant-time via hash)."""
    return hmac.compare_digest(
        hashlib.sha256(a.encode("utf-8")).digest(),
        hashlib.sha256(b.encode("utf-8")).digest(),
    )


def check_credentials(user, password, expected_user, expected_pass):
    """Username: tanpa spasi tepi & tak peka huruf besar (keyboard HP sering kapital).
    Password: persis (peka huruf besar, spasi dihitung)."""
    user_ok = _same((user or "").strip().casefold(), expected_user.strip().casefold())
    pass_ok = verify_password(password or "", expected_pass)
    return user_ok and pass_ok


@st.cache_resource
def _login_throttle():
    return {"lock": threading.Lock(), "fails": 0, "last_fail": 0.0, "locked_until": 0.0}


def throttle_wait(state, now):
    """Sisa detik terkunci (0 kalau tidak terkunci)."""
    with state["lock"]:
        return max(0, int(state["locked_until"] - now + 0.999))


def throttle_record(state, success, now):
    with state["lock"]:
        if success:
            state["fails"] = 0
            state["locked_until"] = 0.0
            return
        if now - state["last_fail"] > LOGIN_FAIL_WINDOW:
            state["fails"] = 0
        state["fails"] += 1
        state["last_fail"] = now
        if state["fails"] >= LOGIN_MAX_FAILS:
            state["locked_until"] = now + LOGIN_LOCK_SECONDS
            state["fails"] = 0


def attempt_login(user, password, state, now, expected):
    """Return (ok, pesan). Saat terkunci, password benar pun ditolak."""
    wait = throttle_wait(state, now)
    if wait > 0:
        return False, f"Terlalu banyak percobaan gagal. Coba lagi dalam {wait} detik."
    if not (user or "").strip() or not password:
        return False, "Isi username dan password terlebih dahulu."
    ok = check_credentials(user, password, expected[0], expected[1])
    throttle_record(state, ok, now)
    if ok:
        return True, ""
    wait = throttle_wait(state, now)
    if wait > 0:
        return False, f"Terlalu banyak percobaan gagal. Coba lagi dalam {wait} detik."
    with state["lock"]:
        left = max(0, LOGIN_MAX_FAILS - state["fails"])
    return False, f"Username atau password salah. Sisa percobaan: {left}."


LOGIN_CSS = """
<style>
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {display: none !important;}
.stApp {
    background:
        radial-gradient(900px 480px at 12% -8%, rgba(37,99,235,.18), transparent 60%),
        radial-gradient(800px 460px at 100% 0%, rgba(13,148,136,.16), transparent 60%);
}
.block-container {
    max-width: 460px !important; margin: 0 auto;
    padding-top: clamp(2rem, 9vh, 5.5rem) !important;
}
.login-brand {text-align: center; margin-bottom: 1.1rem;}
.login-logo {
    width: 68px; height: 68px; margin: 0 auto 0.8rem; border-radius: 20px;
    display: flex; align-items: center; justify-content: center; font-size: 2rem;
    background: linear-gradient(135deg, #2563EB, #0D9488);
    box-shadow: 0 10px 28px rgba(37,99,235,.35);
}
.login-title {font-size: 1.6rem; font-weight: 800; letter-spacing: -0.01em;}
.login-sub {opacity: .9; font-size: .95rem; margin-top: .25rem;}
.st-key-login_card {
    border: 1px solid rgba(128,128,128,.28); border-radius: 18px;
    padding: 1.2rem 1.2rem .6rem; background: rgba(128,128,128,.07);
    box-shadow: 0 12px 36px rgba(0,0,0,.10);
}
.st-key-login_card [data-testid="stForm"] {border: none !important; padding: 0 !important;}
.st-key-login_card [data-testid="stCaptionContainer"] {text-align: center;}
.st-key-login_card button[kind="primaryFormSubmit"],
.st-key-login_card [data-testid="stBaseButton-primaryFormSubmit"],
.st-key-login_card [data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #2563EB, #0D9488) !important;
    color: #fff !important; border: none !important; font-weight: 700;
    min-height: 2.9rem; border-radius: 12px;
}
</style>
"""

LOGIN_BRAND_HTML = """
<div class="login-brand">
    <div style="max-width:300px;margin:0 auto"><!--DEV_BADGE--></div>
    <div class="login-logo">⚡</div>
    <div class="login-title">Routing &amp; Extractor</div>
    <div class="login-sub">Masuk untuk melanjutkan ke Routing Optimizer dan Maps Extractor</div>
</div>
"""
LOGIN_BRAND_HTML = LOGIN_BRAND_HTML.replace("<!--DEV_BADGE-->", DEV_BADGE_HTML)



def render_login_page():
    ss = st.session_state
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)
    st.markdown(LOGIN_BRAND_HTML, unsafe_allow_html=True)
    nonce = ss.get("login_nonce", 0)
    if _auth_credentials() is None:
        with st.container(key="login_card"):
            st.error("Login belum diatur, jadi aplikasi terkunci.")
            st.markdown(
                "Pemilik aplikasi: isi **Secrets** (Streamlit Cloud: *App → Settings → Secrets*) dengan "
                "`APP_USERNAME` dan `APP_PASSWORD_HASH`, lalu muat ulang halaman. Panduan ada di `SETUP_LOGIN.md`."
            )
        return
    with st.container(key="login_card"):
        with st.form("login_form", clear_on_submit=False):
            user = st.text_input(
                "Username", key="login_user", placeholder="Username",
                autocomplete="username",
            )
            password = st.text_input(
                "Password", type="password", key=f"login_pass_{nonce}",
                placeholder="Password", autocomplete="current-password",
            )
            submitted = st.form_submit_button("🔐 Masuk", type="primary", width="stretch")
        if submitted:
            expected = _auth_credentials()
            ok, msg = attempt_login(user, password, _login_throttle(), time.time(), expected)
            if ok:
                ss["auth_ok"] = True
                ss["auth_user"] = expected[0]
                ss["auth_token"] = auth_session_create(expected[0], time.time())
                _auth_set_url(ss["auth_token"])
                ss.pop("no_autologin", None)
                ss.pop("login_flash", None)
                st.rerun()
            else:
                ss["login_flash"] = msg
                ss["login_nonce"] = nonce + 1  # kosongkan kolom password
                st.rerun()
        flash = ss.pop("login_flash", None)
        if flash:
            if flash.startswith("Sesi berakhir"):
                st.info(flash)
            elif flash.startswith("Terlalu banyak"):
                st.warning(flash)
            else:
                st.error(flash)
        st.caption("🔒 Login tetap aktif saat halaman di-refresh. Keluar otomatis bila tidak digunakan lebih dari 30 menit atau tab ditutup.")


def _cookie_js(token):
    """Hapus cookie login versi lama (rp_auth) bila masih ada di browser."""
    body = f"d.cookie='{AUTH_COOKIE}=; path=/; max-age=0; SameSite=Lax';"
    script = f"<script>try{{var d=document;{body}}}catch(e){{}}</script>"
    try:
        import inspect
        if "unsafe_allow_javascript" in inspect.signature(st.html).parameters:
            st.html(script, unsafe_allow_javascript=True)
            return
    except Exception:
        pass
    try:
        import streamlit.components.v1 as components
        components.html(f"<script>try{{var d=window.parent.document;{body}}}catch(e){{}}</script>", height=0)
    except Exception:
        pass

# ================================================================
# PENYIMPANAN SESI OTOMATIS (Supabase lewat REST/PostgREST)
# Cookie `rp_sid` (ID acak) menautkan browser ke satu baris di tabel `rp_sessions`. Tiap ada perubahan berarti, isi sesi
# (file + data Extractor + edit + pengaturan) disimpan terkompresi; saat halaman dibuka lagi dalam keadaan kosong,
# pengguna ditawari memulihkannya. Tanpa kredensial Supabase di secrets, fitur ini mati dan aplikasi berjalan seperti biasa.
# ================================================================
PERSIST_COOKIE = "rp_sid"
PERSIST_PARAM = "rps"      # cadangan: ID sesi juga di URL (?rps=...), ikut terbawa saat refresh walau cookie gagal dipasang
PERSIST_TTL_DAYS = 14
PERSIST_MAX_BYTES = 8 * 1024 * 1024        # batas ukuran terkompresi per sesi
PERSIST_TABLE = "rp_sessions"
_SID_RE = re.compile(r"^[A-Za-z0-9_-]{32,64}$")


@st.cache_resource
def _persist_shared():
    """Keadaan bersama antar-rerun & antar-pengguna di satu proses server: pemutus sirkuit dan jadwal pembersihan.
    (Variabel biasa tidak cukup: skrip dijalankan ulang dari nol tiap interaksi.)"""
    return {"fail_until": 0.0, "last_cleanup": 0.0}


def _persist_conf():
    """(url, key) dari st.secrets['supabase'] (url, service_key) atau env SUPABASE_URL / SUPABASE_SERVICE_KEY; None bila belum diatur."""
    url = key = None
    try:
        sec = st.secrets.get("supabase")
        if sec:
            url, key = sec.get("url"), sec.get("service_key")
    except Exception:
        pass
    url = url or os.environ.get("SUPABASE_URL")
    key = key or os.environ.get("SUPABASE_SERVICE_KEY")
    if not (isinstance(url, str) and url.startswith("http") and isinstance(key, str) and key):
        return None
    return url.rstrip("/"), key


def persist_enabled():
    return _persist_conf() is not None


def _persist_max_bytes():
    """Batas ukuran terkompresi per sesi: secrets supabase.max_mb bila ada, selain itu PERSIST_MAX_BYTES."""
    try:
        mb = float(st.secrets.get("supabase", {}).get("max_mb", 0))
        if mb > 0:
            return int(mb * 1024 * 1024)
    except Exception:
        pass
    return PERSIST_MAX_BYTES


def _sb(method, params=None, body=None, prefer=None, timeout=(3, 8)):
    conf = _persist_conf()
    if conf is None:
        raise RuntimeError("Supabase belum diatur")
    url, key = conf
    headers = {"apikey": key, "Content-Type": "application/json"}
    if not key.startswith("sb_"):
        # Kunci lama (JWT service_role) juga dikirim sebagai Bearer. Kunci baru sb_secret_... BUKAN JWT dan tidak boleh
        # ada di header Authorization (ditolak Supabase) — cukup di header apikey.
        headers["Authorization"] = f"Bearer {key}"
    if prefer:
        headers["Prefer"] = prefer
    return requests.request(method, f"{url}/rest/v1/{PERSIST_TABLE}", params=params, json=body, headers=headers, timeout=timeout)


def _sb_error(r):
    """Ringkas galat Supabase/PostgREST: 'HTTP 403 - permission denied for table rp_sessions (42501)' + petunjuk bila dikenal."""
    msg = code = ""
    try:
        j = r.json()
        if isinstance(j, dict):
            msg, code = str(j.get("message") or j.get("error") or ""), str(j.get("code") or "")
    except Exception:
        pass
    out = f"HTTP {r.status_code}"
    if msg:
        out += f" - {msg[:160]}" + (f" ({code})" if code else "")
    hint = ""
    if r.status_code == 403 or code == "42501":
        hint = " -> jalankan ulang supabase_setup.sql (bagian GRANT untuk service_role)"
    elif r.status_code == 401:
        hint = " -> secret key salah/kedaluwarsa; salin ulang dari Project Settings -> API Keys"
    elif r.status_code == 404 or code in ("PGRST205", "42P01"):
        hint = " -> tabel rp_sessions belum dibuat atau URL proyek salah; jalankan supabase_setup.sql"
    return out + hint


def persist_save(sid, raw, meta):
    """Simpan (upsert) isi sesi. Return (ok, pesan). Pesan 'toobig' = melebihi batas ukuran."""
    if not _SID_RE.match(sid or ""):
        return False, "ID sesi tidak valid"
    comp = gzip.compress(raw, compresslevel=6)
    if len(comp) > _persist_max_bytes():
        return False, "toobig"
    body = {
        "id": sid, "data": base64.b64encode(comp).decode("ascii"), "size_bytes": len(comp), "meta": meta,
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    try:
        r = _sb("POST", params={"on_conflict": "id"}, prefer="resolution=merge-duplicates,return=minimal", body=body)
    except Exception as e:
        return False, f"tidak bisa terhubung ({type(e).__name__})"
    if r.status_code not in (200, 201, 204):
        return False, _sb_error(r)
    return True, ""


def persist_meta(sid):
    """Info ringkas sesi tersimpan tanpa mengunduh isinya. Return ('ok', baris) | ('none', None) | ('error', pesan)."""
    if not _SID_RE.match(sid or ""):
        return "none", None
    try:
        r = _sb("GET", params={"id": f"eq.{sid}", "select": "updated_at,size_bytes,meta"})
    except Exception as e:
        return "error", f"tidak bisa terhubung ({type(e).__name__})"
    if r.status_code != 200:
        return "error", _sb_error(r)
    try:
        rows = r.json()
    except Exception:
        return "error", "balasan Supabase tidak terbaca"
    if rows and isinstance(rows[0], dict):
        return "ok", rows[0]
    return "none", None


def persist_load(sid):
    """Isi sesi (bytes JSON) atau None. Ukuran hasil dekompresi dibatasi MAX_SESSION_BYTES."""
    if not _SID_RE.match(sid or ""):
        return None
    try:
        r = _sb("GET", params={"id": f"eq.{sid}", "select": "data"}, timeout=(3, 20))
        rows = r.json() if r.status_code == 200 else []
        if not rows:
            return None
        comp = base64.b64decode(rows[0]["data"])
        raw = gzip.GzipFile(fileobj=io.BytesIO(comp)).read(MAX_SESSION_BYTES + 1)
    except Exception:
        return None
    return raw if len(raw) <= MAX_SESSION_BYTES else None


def persist_delete(sid):
    if not _SID_RE.match(sid or ""):
        return
    try:
        _sb("DELETE", params={"id": f"eq.{sid}"}, timeout=(3, 5))
    except Exception:
        pass


def persist_cleanup():
    """Hapus sesi yang tak disentuh lebih dari PERSIST_TTL_DAYS hari (paling sering sekali per 6 jam per proses)."""
    shared = _persist_shared()
    if time.time() - shared["last_cleanup"] < 6 * 3600:
        return
    shared["last_cleanup"] = time.time()
    cutoff = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=PERSIST_TTL_DAYS)).isoformat()
    try:
        _sb("DELETE", params={"updated_at": f"lt.{cutoff}"}, timeout=(3, 8))
    except Exception:
        pass


def _persist_cookie_js(sid):
    """Pasang (sid) atau hapus (None) cookie ID sesi di browser."""
    if sid:
        body = (f"d.cookie='{PERSIST_COOKIE}={sid}; path=/; SameSite=Lax; max-age={PERSIST_TTL_DAYS * 86400}'"
                "+(location.protocol==='https:'?'; Secure':'');")
    else:
        body = f"d.cookie='{PERSIST_COOKIE}=; path=/; max-age=0; SameSite=Lax';"
    try:
        import inspect
        if "unsafe_allow_javascript" in inspect.signature(st.html).parameters:
            st.html(f"<script>try{{var d=document;{body}}}catch(e){{}}</script>", unsafe_allow_javascript=True)
            return
    except Exception:
        pass
    try:
        import streamlit.components.v1 as components
        components.html(f"<script>try{{var d=window.parent.document;{body}}}catch(e){{}}</script>", height=0)
    except Exception:
        pass


def _state_has_data(ss):
    return bool(ss.get("uploaded_store")) or bool(ss.get("extracted_data"))


def _persist_sig(ss):
    """Sidik jari isi sesi (file diwakili nama+ukuran+hash agar murah dihitung)."""
    files = [(n, len(b), hashlib.blake2b(b, digest_size=16).hexdigest()) for n, b in sorted(ss.uploaded_store.items())]
    rest = _session_payload(ss, with_files=False)
    return hashlib.sha256(json.dumps([files, rest], sort_keys=True, default=str).encode("utf-8")).hexdigest()


def _ago(iso):
    try:
        dt = datetime.datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        sec = max(0, (datetime.datetime.now(datetime.timezone.utc) - dt).total_seconds())
    except Exception:
        return "beberapa waktu lalu"
    if sec < 60:
        return "baru saja"
    if sec < 3600:
        return f"{int(sec // 60)} menit lalu"
    if sec < 86400:
        return f"{int(sec // 3600)} jam lalu"
    return f"{int(sec // 86400)} hari lalu"


def _check_saved_session():
    """Cek apakah sesi tersimpan untuk ID ini ada; hasilnya masuk persist_offer (ada) atau persist_check_error (gagal dicek)."""
    ss = st.session_state
    ss.persist_offer, ss.persist_check_error = None, None
    if _state_has_data(ss):
        return
    state, val = persist_meta(ss.persist_sid)
    if state == "ok":
        ss.persist_offer = val
    elif state == "error":
        ss.persist_check_error = val


def _persist_sync_url(sid):
    """Selaraskan parameter URL ?rps= dengan ID sesi (tanpa JavaScript; tetap ada saat halaman di-refresh)."""
    try:
        if st.query_params.get(PERSIST_PARAM) != sid:
            st.query_params[PERSIST_PARAM] = sid
    except Exception:
        pass


def init_persistence():
    """Tentukan ID sesi (dari cookie, atau dari URL bila cookie tidak ada) dan, kalau sesi masih kosong, cek sesi tersimpan untuk ditawarkan."""
    ss = st.session_state
    if not persist_enabled():
        return
    if "persist_sid" in ss:
        if not ss.get("persist_cookie_seen"):
            _persist_cookie_js(ss.persist_sid)   # browser belum terbukti menyimpan cookie: pasang lagi (aman diulang)
        _persist_sync_url(ss.persist_sid)
        return
    cookie = param = None
    if not ss.get("persist_ignore_cookie"):
        try:
            cookie = st.context.cookies.get(PERSIST_COOKIE)
        except Exception:
            cookie = None
        try:
            param = st.query_params.get(PERSIST_PARAM)
        except Exception:
            param = None
    cookie_ok = isinstance(cookie, str) and bool(_SID_RE.match(cookie))
    param_ok = isinstance(param, str) and bool(_SID_RE.match(param))
    if cookie_ok or param_ok:
        ss.persist_sid = cookie if cookie_ok else param
        ss.persist_cookie_seen = cookie_ok
        ss.persist_sid_source = "cookie" if cookie_ok else "url"
        _check_saved_session()
        _persist_cookie_js(ss.persist_sid)       # (ulang) pasang cookie & perpanjang masa berlakunya (14 hari)
    else:
        ss.persist_sid = pysecrets.token_urlsafe(24)
        ss.persist_cookie_seen = False
        ss.persist_sid_source = "baru"
        ss.persist_offer = None
        _persist_cookie_js(ss.persist_sid)
    _persist_sync_url(ss.persist_sid)


def _persist_restore():
    ss = st.session_state
    raw = persist_load(ss.get("persist_sid"))
    if raw is None:
        ss.persist_msg = ("error", "Sesi tersimpan tidak bisa dimuat (mungkin sudah kedaluwarsa atau koneksi bermasalah).")
        ss.persist_offer = None
        return
    ok, msg = load_session_bytes(raw)
    ss.persist_offer = None
    ss.persist_msg = ("ok" if ok else "error", ("Sesi dipulihkan. " + msg) if ok else msg)
    if ok:
        ss.persist_last_sig = _persist_sig(ss)           # isi sama dengan yang tersimpan: jangan unggah ulang
        ss.session_saved_sig = _work_sig(ss)
        ss.persist_status = ("saved", time.time())


def _persist_discard():
    ss = st.session_state
    persist_delete(ss.get("persist_sid"))
    ss.persist_offer = None


def _persist_recheck():
    _check_saved_session()


def _persist_skip_check():
    st.session_state.persist_check_error = None


def render_restore_offer():
    ss = st.session_state
    msg = ss.pop("persist_msg", None)
    if msg:
        (st.success if msg[0] == "ok" else st.error)(msg[1])
    err = ss.get("persist_check_error")
    if err and not _state_has_data(ss):
        with st.container(border=True):
            st.warning(f"Tidak bisa memeriksa sesi tersimpan di Supabase: {err}")
            e1, e2 = st.columns(2)
            e1.button("🔄 Coba lagi", key="_persist_recheck", on_click=_persist_recheck, width="stretch")
            e2.button("Lewati, mulai baru", key="_persist_skip", on_click=_persist_skip_check, width="stretch",
                      help="Simpan otomatis lalu jalan seperti biasa; sesi lama (bila ada) akan tertimpa.")
        return
    offer = ss.get("persist_offer")
    if not offer:
        return
    if _state_has_data(ss):          # pengguna sudah mulai bekerja: tawaran tidak relevan lagi
        ss.persist_offer = None
        return
    meta = offer.get("meta") or {}
    bits = []
    if meta.get("files"):
        bits.append(f"{meta['files']} file")
    if meta.get("extracted"):
        bits.append(f"{meta['extracted']} data Maps Extractor")
    if meta.get("edits"):
        bits.append(f"{meta['edits']} edit tabel")
    what = ", ".join(bits) if bits else "data dan pengaturan"
    with st.container(border=True):
        st.markdown(f"💾 **Ada sesi tersimpan** — {what}; disimpan {_ago(offer.get('updated_at'))}.")
        c1, c2 = st.columns(2)
        c1.button("♻️ Pulihkan sesi", key="_persist_restore", type="primary", on_click=_persist_restore, width="stretch")
        c2.button("Mulai baru", key="_persist_discard", on_click=_persist_discard, width="stretch")


def autosave_session():
    """Simpan otomatis bila isi sesi berubah. Gagal tidak mengganggu aplikasi; setelah gagal, jeda 60 detik sebelum mencoba lagi."""
    ss = st.session_state
    if not persist_enabled() or "persist_sid" not in ss:
        return
    if ss.get("persist_offer") or ss.get("persist_check_error") or not _state_has_data(ss):
        return                         # jangan menimpa sesi tersimpan sebelum pengguna memutuskan / dengan sesi kosong
    if time.time() < _persist_shared()["fail_until"]:
        return
    try:
        sig = _persist_sig(ss)
        if sig == ss.get("persist_last_sig"):
            return
        raw = build_session_bytes()
    except Exception:
        return
    n_edits = len(ss.data_edits.get("deleted", [])) + sum(len(c) for c in ss.data_edits.get("changed", {}).values())
    meta = {"files": len(ss.uploaded_store), "extracted": len(ss.extracted_data), "edits": n_edits}
    ok, err = persist_save(ss.persist_sid, raw, meta)
    if ok:
        ss.persist_last_sig = sig
        ss.session_saved_sig = _work_sig(ss)     # data & edit kini tersimpan: tidak lagi dihitung "belum tersimpan"
        ss.persist_status = ("saved", time.time())
        persist_cleanup()
    elif err == "toobig":
        ss.persist_last_sig = sig                # jangan hitung ulang sampai isinya berubah
        ss.persist_status = ("toobig", time.time())
    else:
        _persist_shared()["fail_until"] = time.time() + 60
        ss.persist_status = ("error", err)


def _persist_run_test():
    ss = st.session_state
    try:
        r = _sb("GET", params={"select": "id", "limit": "1"})
        ss.persist_diag = ("ok", "Koneksi & izin tabel OK (HTTP %s)." % r.status_code) if r.status_code == 200 \
            else ("error", _sb_error(r))
    except Exception as e:
        ss.persist_diag = ("error", f"tidak bisa terhubung ({type(e).__name__}: {str(e)[:120]})")


def persist_caption_text():
    """Baris status simpan otomatis ('' bila fitur mati atau belum ada status)."""
    ss = st.session_state
    if not persist_enabled():
        return ""
    st_, val = ss.get("persist_status", (None, None))
    if st_ == "saved":
        return f"☁️ Tersimpan otomatis · {_ago(datetime.datetime.fromtimestamp(val, datetime.timezone.utc).isoformat())}"
    if st_ == "toobig":
        return f"ℹ️ Sesi terlalu besar (> {max(1, round(_persist_max_bytes() / (1024 * 1024)))} MB) untuk disimpan otomatis."
    if st_ == "error":
        return f"⚠️ Simpan otomatis tertunda: {val}. Akan dicoba lagi."
    return ""


def render_persist_caption(slot):
    """Isi/perbarui slot status. Dipanggil SETELAH autosave_session (awal & akhir skrip), jadi status selalu yang terbaru."""
    txt = persist_caption_text()
    if txt:
        slot.caption(txt)
    else:
        slot.empty()


def render_persist_diag():
    ss = st.session_state
    if not persist_enabled():
        return
    with st.expander("🔧 Diagnosa simpan otomatis", expanded=False):
        sid = ss.get("persist_sid") or ""
        st.caption("Cookie ID sesi: " + ("✅ terbaca dari browser saat halaman dibuka" if ss.get("persist_cookie_seen")
                                         else "⚠️ belum terbaca saat halaman dibuka (cadangan lewat URL aktif)"))
        st.caption({"cookie": "Sumber ID: cookie", "url": "Sumber ID: URL (?rps=)", "baru": "Sumber ID: baru dibuat"}.get(ss.get("persist_sid_source"), "Sumber ID: -"))
        st.caption(f"ID sesi: `{sid[:6]}…`" if sid else "ID sesi: belum ada")
        st.button("Tes koneksi Supabase", key="_persist_test", on_click=_persist_run_test, width="stretch")
        d = ss.get("persist_diag")
        if d:
            (st.success if d[0] == "ok" else st.error)(d[1])


auth_refresh()

if not st.session_state.get("auth_ok"):
    if st.session_state.pop("clear_cookie", False):
        _cookie_js(None)
        _persist_cookie_js(None)
        _leave_guard_js(False)   # logout: lepas konfirmasi refresh supaya tidak muncul di halaman login
    elif st.session_state.pop("auth_expired", False):
        _leave_guard_js(False)   # login kedaluwarsa: konfirmasi refresh juga dilepas di halaman login
    render_login_page()
    render_footer()
    st.stop()




def _logout():
    ss = st.session_state
    if ss.get("auth_token"):
        auth_session_end(ss["auth_token"])     # token login di server dicabut
    if persist_enabled() and ss.get("persist_sid"):
        persist_delete(ss["persist_sid"])      # keluar = akhiri sesi tersimpan juga
    keep = {k: ss[k] for k in ("view_mode", "app_mode") if k in ss}
    ss.clear()
    ss.update(keep)
    try:
        st.query_params.pop(PERSIST_PARAM, None)   # ID sesi & token login di URL ikut dibersihkan
        st.query_params.pop(AUTH_PARAM, None)
    except Exception:
        pass
    ss["no_autologin"] = True   # token lama bisa masih ada di URL sesi ini
    ss["persist_ignore_cookie"] = True   # begitu juga cookie ID sesi
    ss["clear_cookie"] = True


def render_user_bar(prefix, compact=False):
    user = st.session_state.get("auth_user", "")
    help_txt = "Keluar dan hapus semua data di sesi ini. Simpan sesi dulu kalau masih dipakai."
    if compact:
        with st.container(key="userrow"):
            c1, c2 = st.columns([2, 1])
            c1.markdown(f"👤 **{user}**")
            c2.button("🚪 Keluar", key=f"logout_{prefix}", on_click=_logout,
                      help=help_txt, width="stretch")
    else:
        st.caption(f"👤 Masuk sebagai **{user}**")
        st.button("🚪 Keluar", key=f"logout_{prefix}", on_click=_logout,
                  help=help_txt, width="stretch")


SPLIT_FULL = "📦 Isi penuh"
SPLIT_AUTO = "🧭 Otomatis (per area)"
if "split_mode_flag" not in st.session_state:
    st.session_state.split_mode_flag = SPLIT_AUTO


def _sync_split():
    st.session_state.split_mode_flag = st.session_state.get(_wk(_wk("_split_widget")), st.session_state.split_mode_flag)


def _fmt_sizes(sizes):
    shown = " + ".join(str(x) for x in sizes[:5])
    return shown + (" + …" if len(sizes) > 5 else "")


if "round_trip_flag" not in st.session_state:
    st.session_state.round_trip_flag = False
if "dedupe_flag" not in st.session_state:
    st.session_state.dedupe_flag = True


def _sync_round_trip():
    # .get() with a fallback — not direct attribute access — because
    # "Buka Sesi" / preset deliberately bump the widget key version to force a refresh,
    # and if that happens to land in the same batch as this callback
    # (e.g. the user edits a field then immediately clicks "Buka Sesi"
    # before it blurs), the key can be briefly missing. Attribute access
    # would crash the whole app in that case; .get() just no-ops safely.
    st.session_state.round_trip_flag = st.session_state.get(
        _wk("_round_trip_widget"), st.session_state.round_trip_flag
    )


def _sync_dedupe():
    st.session_state.dedupe_flag = st.session_state.get(
        _wk("_dedupe_widget"), st.session_state.dedupe_flag
    )


def _sync_use_extracted():
    st.session_state.use_extracted_flag = st.session_state.get(
        _wk("_use_extracted_widget"), st.session_state.use_extracted_flag
    )


def _sync_nearest_on():
    st.session_state.nearest_on_flag = bool(st.session_state.get(_wk("_nearest_on_widget")))


def _sync_nearest_n():
    try:
        st.session_state.nearest_n_flag = max(2, int(st.session_state.get(_wk("_nearest_n_widget"), 20)))
    except (TypeError, ValueError):
        pass


def pick_nearest(df, lat, lon, n):
    """N baris terdekat (jarak garis lurus) dari (lat, lon). Return (df_terpilih_urutan_asli, info) atau (df, None) bila tak perlu."""
    if n >= len(df):
        return df, None
    d = np.array([haversine(lat, lon, a, b) for a, b in zip(df["latitude"], df["longitude"])])
    keep = np.sort(np.argsort(d, kind="stable")[:n])
    return df.iloc[keep].reset_index(drop=True), {"picked": int(n), "total": int(len(df)), "max_km": float(d[keep].max())}


def _sync_starting_link():
    st.session_state.starting_link_saved = st.session_state.get(
        _wk("_starting_link_widget"), st.session_state.starting_link_saved
    )


START_MODE_LABELS = {"manual": "✍️ Tentukan titik awal", "mylocation": "📍 Lokasi anda"}


def _sync_start_mode():
    """Kotak centang "navigasi mulai dari lokasi petugas": disimpan sebagai start_mode_saved = 'mylocation' / 'manual'."""
    ss = st.session_state
    ss.start_mode_saved = "mylocation" if ss.get(_wk("_start_mode_widget")) else "manual"


def _step_next(key, n):
    """Tombol "Titik berikutnya": geser pilihan titik navigasi satu langkah (maksimal sampai titik terakhir)."""
    ss = st.session_state
    ss[key] = min(int(ss.get(key, 0)) + 1, max(0, n - 1))


# ---- Mode Lapangan: satu titik per layar untuk petugas ------------------------------------------------------
FIELD_ICONS = {"done": "✅", "skip": "⏭️"}


def field_stops(r):
    """Titik kunjungan sebuah rute berurutan (tanpa titik awal tetap). Tiap titik punya 'sig' unik (tahan urutan manual)."""
    df = r["df"]
    seen, out = {}, []
    for _, row in df.iloc[1 if r.get("has_start") else 0:].iterrows():
        base = f"{r['route_id']}|{_row_sig(row['merchant_name'], row['latitude'], row['longitude'])}"
        k = seen.get(base, 0)
        seen[base] = k + 1
        out.append({
            "sig": f"{base}#{k}", "seq": int(row["sequence"]), "name": str(row["merchant_name"]),
            "lat": float(row["latitude"]), "lon": float(row["longitude"]),
            "eta": str(row["jam_tiba"]) if "jam_tiba" in df.columns and row.get("jam_tiba") else "",
            "note": str(row["jadwal_status"]) if row.get("jadwal_status") else "",
            "prio": bool(row.get("prioritas_flag", False)),
        })
    return out


def field_counts(stops, status):
    done = sum(1 for x in stops if status.get(x["sig"]) == "done")
    skip = sum(1 for x in stops if status.get(x["sig"]) == "skip")
    return done, skip, len(stops) - done - skip


def field_current(stops, status, focus_sig=None):
    """Titik yang sedang dituju: titik pilihan 'lompat' bila masih tersisa, selain itu yang pertama belum ditandai."""
    pending = [x for x in stops if x["sig"] not in status]
    if focus_sig:
        for x in pending:
            if x["sig"] == focus_sig:
                return x
    return pending[0] if pending else None


def _field_state(result):
    return result.setdefault("field", {"status": {}, "log": [], "focus": {}})


def _field_mark(result, rid, sig, kind):
    fs = _field_state(result)
    fs["status"][sig] = kind
    fs["log"].append(sig)
    fs["focus"].pop(rid, None)


def _field_undo(result, rid):
    fs = _field_state(result)
    if fs["log"]:
        sig = fs["log"].pop()
        fs["status"].pop(sig, None)
        fs["focus"][rid] = sig          # kembali ke titik yang baru dibatalkan


def _field_reset(result, sigs):
    fs = _field_state(result)
    for sg in sigs:
        fs["status"].pop(sg, None)
    fs["log"] = [x for x in fs["log"] if x in fs["status"]]
    fs["focus"].clear()


def _field_jump(result, rid, widget_key):
    sig = st.session_state.get(widget_key)
    if sig:
        _field_state(result)["focus"][rid] = sig


def render_field_mode(route_summaries, result):
    """Tampilan satu-titik-per-layar: kartu titik sekarang, tombol navigasi besar, Selesai / Lewati, progres."""
    st.caption("📱 Tampilan sederhana untuk di lapangan: satu titik per layar. Penanda selesai/lewati tersimpan selama hasil rute ini "
               "masih ada (hilang saat rute dibuat ulang atau halaman di-refresh).")
    if len(route_summaries) > 1:
        rid = st.selectbox(
            "Rute", options=[x["route_id"] for x in route_summaries], key="_field_route",
            format_func=lambda i: next(
                f"Rute {x['route_id'] + 1}" + (f" — {x['driver']}" if x.get("driver") else "")
                + (f" · {fmt_day_label(datetime.date.fromisoformat(x['tanggal']))}" if x.get("tanggal") else "")
                for x in route_summaries if x["route_id"] == i),
        )
        r = next(x for x in route_summaries if x["route_id"] == rid)
    else:
        r = route_summaries[0]
        rid = r["route_id"]
    stops = field_stops(r)
    if not stops:
        st.info("Rute ini tidak punya titik kunjungan.")
        return
    fs = _field_state(result)
    status = fs["status"]
    done, skip, left = field_counts(stops, status)
    st.progress((done + skip) / len(stops))
    st.caption(f"✅ {done} selesai · ⏭️ {skip} dilewati · 🕓 {left} tersisa dari {len(stops)} titik")
    cur = field_current(stops, status, fs["focus"].get(rid))
    if cur is None:
        st.success("🎉 Semua titik pada rute ini sudah ditandai.")
        if r.get("round_trip"):
            st.caption("↩️ Rute ini pulang-pergi: jangan lupa kembali ke titik awal.")
    else:
        pos = next(i for i, x in enumerate(stops) if x["sig"] == cur["sig"]) + 1
        with st.container(border=True):
            st.markdown(f"<div style='font-size:.9rem;opacity:.8'>Titik {pos} dari {len(stops)} · urutan #{cur['seq']}</div>",
                        unsafe_allow_html=True)
            st.markdown(
                f"<div style='font-size:1.7rem;font-weight:800;line-height:1.25;margin:2px 0 6px'>"
                f"{'⭐ ' if cur['prio'] else ''}{html_lib.escape(cur['name'])}</div>",
                unsafe_allow_html=True,
            )
            meta = []
            if cur["eta"]:
                meta.append(f"⏰ Perkiraan tiba {html_lib.escape(cur['eta'])}")
            if cur["note"] and cur["note"] != "✅":
                meta.append(html_lib.escape(cur["note"]))
            if meta:
                st.markdown("<div style='font-size:1rem;margin-bottom:6px'>" + " · ".join(meta) + "</div>", unsafe_allow_html=True)
            with st.container(key=f"fm_nav_{rid}"):
                st.link_button("🧭 Navigasi ke titik ini", stop_nav_url(cur["lat"], cur["lon"]), type="primary", width='stretch')
            with st.container(key=f"fmrow_main_{rid}"):
                b1, b2 = st.columns(2)
                b1.button("✅ Selesai", key=f"_fm_done_{rid}", width='stretch', on_click=_field_mark, args=(result, rid, cur["sig"], "done"))
                b2.button("⏭️ Lewati", key=f"_fm_skip_{rid}", width='stretch', on_click=_field_mark, args=(result, rid, cur["sig"], "skip"))
        nxt = next((x for x in stops if x["sig"] not in status and x["sig"] != cur["sig"]), None)
        if nxt:
            st.caption(f"Berikutnya: **{nxt['name']}**" + (f" · ±{nxt['eta']}" if nxt["eta"] else ""))
    with st.container(key=f"fmrow_aux_{rid}"):
        c1, c2 = st.columns(2)
        c1.button("↩️ Urungkan", key=f"_fm_undo_{rid}", width='stretch', disabled=not fs["log"],
                  on_click=_field_undo, args=(result, rid))
        c2.button("🔄 Mulai ulang", key=f"_fm_reset_{rid}", width='stretch', disabled=not status,
                  on_click=_field_reset, args=(result, [x["sig"] for x in stops]))
    with st.expander("📋 Daftar titik & lompat ke titik lain"):
        pend = [x for x in stops if x["sig"] not in status]
        if pend:
            st.selectbox(
                "Lompat ke titik (yang belum ditandai)", options=[x["sig"] for x in pend], key=f"_fm_jump_{rid}",
                format_func=lambda sg, _p=pend: next(f"{x['seq']}. {x['name']}" for x in _p if x["sig"] == sg),
                index=None, placeholder="Pilih titik…", on_change=_field_jump, args=(result, rid, f"_fm_jump_{rid}"),
            )
        with st.container(height=260):
            for x in stops:
                icon = FIELD_ICONS.get(status.get(x["sig"]), "🕓")
                mark = "👉 " if cur and x["sig"] == cur["sig"] else ""
                st.markdown(f"{mark}{icon} {x['seq']}. {x['name']}" + (f" · {x['eta']}" if x["eta"] else ""))


def _map_set_status(row_key):
    """Callback tombol di pratinjau peta: simpan status baru sebagai edit data (sama seperti edit tabel)."""
    ss = st.session_state
    new_status = ss.get(f"_map_status_{row_key}")
    if new_status not in STATUS_OPTIONS:
        return
    ss.data_edits["changed"].setdefault(row_key, {})["status"] = new_status
    ss.data_edit_nonce += 1
    ss.map_panel_open = True


def _map_delete_row(row_key):
    """Callback tombol di pratinjau peta: hapus merchant dari data (sama seperti centang Hapus di tabel)."""
    ss = st.session_state
    ss.data_edits["deleted"] = sorted(set(ss.data_edits["deleted"]) | {row_key})
    ss.data_edits["changed"].pop(row_key, None)
    ss.data_edit_nonce += 1
    ss.map_selected_key = None
    ss.map_panel_open = True


def _sync_exclude_outliers():
    st.session_state.exclude_outliers_flag = st.session_state.get(
        _wk("_exclude_outliers_widget"), st.session_state.exclude_outliers_flag
    )


def _sync_hours_opt():
    st.session_state.hours_opt_flag = st.session_state.get(
        _wk("_hours_opt_widget"), st.session_state.hours_opt_flag
    )
    st.session_state.table_panel_open = True   # kotak centangnya ada di panel data; jangan menutupnya


def _sync_balance_time():
    st.session_state.balance_time_flag = st.session_state.get(
        _wk("_balance_time_widget"), st.session_state.balance_time_flag
    )


def _sync_geo_city():
    st.session_state.geocode_city = st.session_state.get(
        _wk("_geo_city_widget"), st.session_state.geocode_city
    )


def _sync_use_multi_depot():
    st.session_state.use_multi_depot_flag = st.session_state.get(
        _wk("_use_multi_depot_widget"), st.session_state.use_multi_depot_flag
    )


PLAN_MAX = "📏 Maksimal titik per rute"
PLAN_COUNT = "👥 Jumlah rute (mis. jumlah sales)"
for _k, _v in {
    "plan_mode_flag": PLAN_COUNT,
    "target_routes_flag": 1,
    "visit_minutes_flag": 0,
    "start_time_flag": datetime.time(8, 0),
    "session_nonce": 0,
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


def _sync_plan():
    st.session_state.plan_mode_flag = st.session_state.get(
        _wk("_plan_widget"), st.session_state.plan_mode_flag
    )


def _sync_target():
    st.session_state.target_routes_flag = int(
        st.session_state.get(_wk("_target_widget"), st.session_state.target_routes_flag)
    )


def _sync_visit():
    st.session_state.visit_minutes_flag = int(
        st.session_state.get(_wk("_visit_widget"), st.session_state.visit_minutes_flag)
    )


def _sync_start_time():
    st.session_state.start_time_flag = st.session_state.get(
        _wk("_start_time_widget"), st.session_state.start_time_flag
    )


# ---------- Simpan / buka sesi ----------
MAX_SESSION_BYTES = 40 * 1024 * 1024
PRESET_MAX = 20


def _set_depot_rows(depot_rows):
    """Ganti seluruh baris titik-awal dengan daftar (nama, lokasi) baru. Id baris selalu
    baru supaya tidak bentrok dengan widget key baris lama."""
    ss = st.session_state
    for rid in ss.multi_depot_rows:
        ss.pop(f"depot_name_{rid}", None)
        ss.pop(f"depot_loc_{rid}", None)
    ss.multi_depot_rows = []
    for name, loc in depot_rows:
        rid = ss.multi_depot_next_id
        ss.multi_depot_next_id += 1
        ss[f"depot_name_{rid}"] = name
        ss[f"depot_loc_{rid}"] = loc
        ss.multi_depot_rows.append(rid)


def _session_payload(ss, with_files=True):
    """Isi sesi sebagai dict (tanpa stempel waktu). with_files=False untuk menghitung sidik jari tanpa meng-encode file."""
    extracted = [
        {k: (None if isinstance(v, float) and math.isnan(v) else v) for k, v in row.items()}
        for row in ss.extracted_data
    ]
    payload = {
        "app": "routing-extractor",
        "version": 1,
        "extracted_data": extracted,
        "settings": {
            "use_extracted_flag": bool(ss.use_extracted_flag),
            "starting_link_saved": ss.starting_link_saved,
            "start_mode_saved": ss.start_mode_saved,
            "nearest_on_flag": bool(ss.nearest_on_flag),
            "nearest_n_flag": int(ss.nearest_n_flag),
            "sheet": ({"link": ss.sheet_sync["link"], "fname": ss.sheet_sync["fname"], "on": bool(ss.sheet_sync["on"])}
                      if ss.get("sheet_sync") else {"link": ss.get("sheet_link_saved", ""), "fname": "", "on": False}),
            "round_trip_flag": bool(ss.round_trip_flag),
            "dedupe_flag": bool(ss.dedupe_flag),
            "split_mode_flag": ss.split_mode_flag,
            "plan_mode_flag": ss.plan_mode_flag,
            "target_routes_flag": int(ss.target_routes_flag),
            "visit_minutes_flag": int(ss.visit_minutes_flag),
            "start_time_flag": ss.start_time_flag.strftime("%H:%M"),
            "multi_depot_rows": [
                {
                    "name": ss.get(f"depot_name_{rid}", ""),
                    "input": ss.get(f"depot_loc_{rid}", ""),
                }
                for rid in ss.multi_depot_rows
            ],
            "use_multi_depot_flag": bool(ss.use_multi_depot_flag),
            "driver_names": {str(k): str(v) for k, v in ss.driver_names.items()},
            "geocode_city": ss.geocode_city,
            "balance_time_flag": bool(ss.balance_time_flag),
            "hours_opt_flag": bool(ss.hours_opt_flag),
            "exclude_outliers_flag": bool(ss.exclude_outliers_flag),
        },
        "data_edits": ss.data_edits,
        "presets": ss.presets,
        "geocode_cache": ss.geocode_cache,
    }
    if with_files:
        payload["files"] = {name: base64.b64encode(data).decode("ascii") for name, data in ss.uploaded_store.items()}
    return payload


def build_session_bytes():
    payload = _session_payload(st.session_state)
    payload["saved_at"] = datetime.datetime.now().isoformat(timespec="seconds")
    return json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")


def load_session_bytes(raw):
    """Muat file sesi. Isi file diperlakukan sebagai data: divalidasi, bukan dijalankan."""
    if len(raw) > MAX_SESSION_BYTES:
        return False, "File sesi terlalu besar."
    try:
        data = json.loads(raw.decode("utf-8-sig"))
    except Exception:
        return False, "File sesi tidak bisa dibaca (bukan JSON yang valid)."
    if not isinstance(data, dict) or data.get("app") != "routing-extractor":
        return False, "File ini bukan file sesi dari aplikasi ini."

    files_raw = data.get("files")
    files = {}
    for name, b64 in (files_raw if isinstance(files_raw, dict) else {}).items():
        if not isinstance(name, str) or not isinstance(b64, str):
            continue
        safe_name = os.path.basename(name) or "data.xlsx"
        try:
            files[safe_name] = base64.b64decode(b64, validate=True)
        except Exception:
            return False, f"File '{safe_name}' di dalam sesi rusak."

    ext_raw = data.get("extracted_data")
    extracted = [
        {str(k): v for k, v in row.items()}
        for row in (ext_raw[:5000] if isinstance(ext_raw, list) else [])
        if isinstance(row, dict)
    ]

    cfg = data.get("settings") if isinstance(data.get("settings"), dict) else {}
    updates = {}
    for key in ("use_extracted_flag", "round_trip_flag", "dedupe_flag"):
        if isinstance(cfg.get(key), bool):
            updates[key] = cfg[key]
    if isinstance(cfg.get("nearest_on_flag"), bool):
        updates["nearest_on_flag"] = cfg["nearest_on_flag"]
    if isinstance(cfg.get("nearest_n_flag"), int) and 2 <= cfg["nearest_n_flag"] <= 100000:
        updates["nearest_n_flag"] = cfg["nearest_n_flag"]
    if cfg.get("start_mode_saved") in ("manual", "mylocation"):
        updates["start_mode_saved"] = cfg["start_mode_saved"]
    _sh = cfg.get("sheet") if isinstance(cfg.get("sheet"), dict) else {}
    _sh_link = _sh.get("link") if isinstance(_sh.get("link"), str) else ""
    _sh_link = _sh_link.strip()[:500] if parse_sheet_link(_sh_link) else ""
    updates["sheet_link_saved"] = _sh_link
    if isinstance(cfg.get("starting_link_saved"), str):
        updates["starting_link_saved"] = cfg["starting_link_saved"][:2000]
    if cfg.get("split_mode_flag") in (SPLIT_AUTO, SPLIT_FULL):
        updates["split_mode_flag"] = cfg["split_mode_flag"]
    if cfg.get("plan_mode_flag") in (PLAN_MAX, PLAN_COUNT):
        updates["plan_mode_flag"] = cfg["plan_mode_flag"]
    if isinstance(cfg.get("target_routes_flag"), int) and 1 <= cfg["target_routes_flag"] <= 10000:
        updates["target_routes_flag"] = cfg["target_routes_flag"]
    if isinstance(cfg.get("visit_minutes_flag"), int) and 0 <= cfg["visit_minutes_flag"] <= 480:
        updates["visit_minutes_flag"] = cfg["visit_minutes_flag"]
    if isinstance(cfg.get("start_time_flag"), str):
        try:
            updates["start_time_flag"] = datetime.datetime.strptime(cfg["start_time_flag"], "%H:%M").time()
        except ValueError:
            pass
    if isinstance(cfg.get("use_multi_depot_flag"), bool):
        updates["use_multi_depot_flag"] = cfg["use_multi_depot_flag"]
    for _bk in ("balance_time_flag", "exclude_outliers_flag", "hours_opt_flag"):
        if isinstance(cfg.get(_bk), bool):
            updates[_bk] = cfg[_bk]
    depot_rows_raw = cfg.get("multi_depot_rows")
    depot_rows = [
        (str(d.get("name", ""))[:120], str(d.get("input", ""))[:500])
        for d in (depot_rows_raw[:50] if isinstance(depot_rows_raw, list) else [])
        if isinstance(d, dict)
    ]
    driver_names_raw = cfg.get("driver_names")
    driver_names = {}
    if isinstance(driver_names_raw, dict):
        for k, v in driver_names_raw.items():
            try:
                driver_names[int(k)] = str(v)[:120]
            except (TypeError, ValueError):
                continue

    presets = {}
    presets_raw = data.get("presets")
    if isinstance(presets_raw, dict):
        for pname, praw in list(presets_raw.items())[:PRESET_MAX]:
            cleaned = _clean_preset(praw)
            if cleaned and isinstance(pname, str) and pname.strip():
                presets[pname.strip()[:40]] = cleaned
    geocode_cache = {}
    cache_raw = data.get("geocode_cache")
    if isinstance(cache_raw, dict):
        for ck, cv in list(cache_raw.items())[:5000]:
            if not isinstance(ck, str) or not isinstance(cv, dict):
                continue
            city_v = str(cv.get("city", ""))[:120]
            try:
                if cv.get("failed") is True:
                    geocode_cache[ck[:400]] = {"failed": True, "city": city_v}
                else:
                    lat_v, lon_v = float(cv["lat"]), float(cv["lon"])
                    if -90 <= lat_v <= 90 and -180 <= lon_v <= 180:
                        geocode_cache[ck[:400]] = {
                            "lat": lat_v, "lon": lon_v,
                            "label": str(cv.get("label", ""))[:300], "city": city_v,
                        }
            except (KeyError, TypeError, ValueError):
                continue

    ss = st.session_state
    ss.uploaded_store = files
    ss.extracted_data = extracted
    ss.driver_names = driver_names
    for k, v in updates.items():
        ss[k] = v
    ss.sheet_sync = None
    _sh_fn = os.path.basename(str(_sh.get("fname") or ""))
    if _sh_link and _sh_fn in files:      # lanjutkan pemantauan Sheet untuk file hasil Sheet
        sheet_sync_start(ss, _sh_link, _sh_fn, files[_sh_fn])
        ss.sheet_sync["on"] = bool(_sh.get("on"))
    ss.widget_nonce += 1  # kunci widget baru -> browser membuat widget baru yang langsung memakai nilai terbaru
    _set_depot_rows(depot_rows)
    ss.data_edits = clean_data_edits(data.get("data_edits"))
    ss.data_edit_nonce += 1
    ss.presets = presets
    ss.geocode_cache = geocode_cache
    if isinstance(cfg.get("geocode_city"), str):
        ss.geocode_city = cfg["geocode_city"][:120]
    ss.route_result = None
    ss.uploader_nonce += 1
    return True, f"Sesi dimuat: {len(files)} file dan {len(extracted)} data Maps Extractor."


# ---------- Preset pengaturan (Mode Pro) ----------
def _clean_preset(raw):
    """Validasi satu preset (dari sesi/file) — hasilnya dict bersih atau None."""
    if not isinstance(raw, dict):
        return None
    try:
        plan_mode = raw.get("plan_mode")
        split_mode = raw.get("split_mode")
        if plan_mode not in (PLAN_MAX, PLAN_COUNT) or split_mode not in (SPLIT_AUTO, SPLIT_FULL):
            return None
        target = int(raw.get("target_routes", 2))
        visit = int(raw.get("visit_minutes", 0))
        if not (1 <= target <= 10000 and 0 <= visit <= 480):
            return None
        start_t = datetime.datetime.strptime(str(raw.get("start_time", "08:00")), "%H:%M").strftime("%H:%M")
    except (TypeError, ValueError):
        return None
    rows_raw = raw.get("depot_rows")
    rows = [
        {"name": str(d.get("name", ""))[:120], "input": str(d.get("input", ""))[:500]}
        for d in (rows_raw[:50] if isinstance(rows_raw, list) else [])
        if isinstance(d, dict)
    ]
    return {
        "plan_mode": plan_mode, "target_routes": target, "split_mode": split_mode,
        "start_time": start_t, "visit_minutes": visit,
        "round_trip": bool(raw.get("round_trip", False)),
        "balance_time": bool(raw.get("balance_time", False)),
        "starting_link": str(raw.get("starting_link", ""))[:2000],
        "use_multi_depot": bool(raw.get("use_multi_depot", False)),
        "depot_rows": rows,
    }


def _current_settings_snapshot():
    ss = st.session_state
    return {
        "plan_mode": ss.plan_mode_flag,
        "target_routes": int(ss.target_routes_flag),
        "split_mode": ss.split_mode_flag,
        "start_time": ss.start_time_flag.strftime("%H:%M"),
        "visit_minutes": int(ss.visit_minutes_flag),
        "round_trip": bool(ss.round_trip_flag),
        "balance_time": bool(ss.balance_time_flag),
        "starting_link": ss.starting_link_saved,
        "use_multi_depot": bool(ss.use_multi_depot_flag),
        "depot_rows": [
            {"name": ss.get(f"depot_name_{rid}", ""), "input": ss.get(f"depot_loc_{rid}", "")}
            for rid in ss.multi_depot_rows
        ],
    }


def describe_preset(p):
    parts = [f"{p['target_routes']} rute" if p["plan_mode"] == PLAN_COUNT else "jumlah rute: maks. titik per rute"]
    parts.append(f"mulai {p['start_time']}")
    parts.append(f"kunjungan {p['visit_minutes']} mnt")
    parts.append("pulang ke titik awal" if p["round_trip"] else "satu arah")
    if p.get("balance_time"):
        parts.append("beban waktu diseimbangkan")
    if p["use_multi_depot"]:
        n = sum(1 for d in p["depot_rows"] if d["input"].strip())
        parts.append(f"multi-depot ({n} titik)")
    elif p["starting_link"].strip():
        parts.append("titik awal terisi")
    return " · ".join(parts)


def _save_preset():
    ss = st.session_state
    name = str(ss.get("_preset_name", "")).strip()[:40]
    if not name:
        ss.preset_flash = ("error", "Isi nama preset dulu.")
        return
    if name not in ss.presets and len(ss.presets) >= PRESET_MAX:
        ss.preset_flash = ("error", f"Maksimal {PRESET_MAX} preset — hapus salah satu dulu.")
        return
    existed = name in ss.presets
    ss.presets[name] = _current_settings_snapshot()
    ss.preset_panel_open = True
    ss["_preset_name"] = ""
    ss["_preset_select"] = name
    ss.preset_flash = ("success", f"Preset “{name}” {'diperbarui' if existed else 'disimpan'}.")


def _apply_preset():
    ss = st.session_state
    name = ss.get("_preset_select")
    preset = _clean_preset(ss.presets.get(name))
    if not preset:
        ss.preset_flash = ("error", "Preset tidak ditemukan atau rusak.")
        return
    ss.plan_mode_flag = preset["plan_mode"]
    ss.target_routes_flag = preset["target_routes"]
    ss.split_mode_flag = preset["split_mode"]
    ss.start_time_flag = datetime.datetime.strptime(preset["start_time"], "%H:%M").time()
    ss.visit_minutes_flag = preset["visit_minutes"]
    ss.round_trip_flag = preset["round_trip"]
    ss.balance_time_flag = preset["balance_time"]
    ss.starting_link_saved = preset["starting_link"]
    ss.use_multi_depot_flag = preset["use_multi_depot"]
    ss.widget_nonce += 1  # kunci widget baru -> browser membuat widget baru yang langsung memakai nilai preset
    ss.preset_panel_open = True
    _set_depot_rows([(d["name"], d["input"]) for d in preset["depot_rows"]])
    ss.preset_flash = ("success", f"Preset “{name}” diterapkan.")


def _delete_preset():
    ss = st.session_state
    name = ss.get("_preset_select")
    if name in ss.presets:
        del ss.presets[name]
        ss.pop("_preset_select", None)
        ss.preset_panel_open = True
        ss.preset_flash = ("success", f"Preset “{name}” dihapus.")


def _keep_preset_panel_open():
    st.session_state.preset_panel_open = True


def render_preset_panel():
    """Simpan / terapkan kombinasi pengaturan bernama. Hanya dipanggil di Mode Pro."""
    ss = st.session_state
    flash = ss.preset_flash
    ss.preset_flash = None
    with st.expander(f"💾 Preset Pengaturan ({len(ss.presets)})", expanded=(flash is not None) or ss.preset_panel_open):
        if flash:
            {"error": st.error, "success": st.success}.get(flash[0], st.info)(flash[1])
        st.caption(
            "Simpan kombinasi pengaturan yang sering dipakai, mis. “Rute Pagi Sales”. Yang tersimpan: "
            "cara & jumlah rute, cara membagi, jam mulai, durasi kunjungan, titik-balik, dan titik awal. "
            "*Maksimal titik per rute* tidak ikut karena batasnya bergantung jumlah merchant. "
            "Preset ikut tersimpan di file **Simpan / Buka Sesi**."
        )
        names = list(ss.presets.keys())
        if names:
            if ss.get("_preset_select") not in names:
                ss.pop("_preset_select", None)
            st.selectbox("Pilih preset", names, key="_preset_select", on_change=_keep_preset_panel_open)
            chosen = _clean_preset(ss.presets.get(ss.get("_preset_select")))
            if chosen:
                st.caption(describe_preset(chosen))
            b1, b2 = st.columns(2)
            with b1:
                st.button("✅ Terapkan", key="_preset_apply", on_click=_apply_preset,
                          type="primary", width="stretch")
            with b2:
                st.button("🗑️ Hapus", key="_preset_delete", on_click=_delete_preset, width="stretch")
            st.markdown("---")
        st.text_input("Nama preset baru", key="_preset_name", max_chars=40,
                      placeholder="mis. Rute Pagi Sales",
                      help="Memakai nama yang sudah ada akan memperbarui preset itu.")
        st.button("💾 Simpan pengaturan saat ini", key="_preset_save", on_click=_save_preset, width="stretch")


def render_session_panel(prefix):
    ss = st.session_state
    flash = ss.pop("_session_flash", None)
    with st.expander("💾 Simpan / Buka Sesi", expanded=flash is not None):
        if flash:
            (st.success if flash[0] == "ok" else st.error)(flash[1])
        st.caption(
            "Simpan data & pengaturan ke satu file untuk dilanjutkan nanti, bahkan setelah halaman "
            "di-refresh. Hasil rute tidak ikut disimpan — tinggal tekan Buat Rute lagi. "
            "File berisi data merchant, jadi simpan di tempat yang aman."
        )
        st.download_button(
            "💾 Simpan sesi",
            data=build_session_bytes(),
            file_name=f"sesi-rute-{datetime.datetime.now():%Y%m%d-%H%M}.json",
            mime="application/json",
            key=f"{prefix}_session_dl",
            on_click=_mark_session_saved,
            width='stretch',
            disabled=not (ss.uploaded_store or ss.extracted_data),
        )
        up = st.file_uploader("📂 Buka sesi (.json)", type=["json"], key=f"{prefix}_session_up_{ss.session_nonce}")
        if up is not None:
            ok, msg = load_session_bytes(up.getvalue())
            ss._session_flash = ("ok" if ok else "err", msg)
            ss.session_nonce += 1
            st.rerun()

# ==========================================================================================
# NAVIGASI + PILIHAN MODE TAMPILAN
# ==========================================================================================
def _set_mode(mode):
    st.session_state.view_mode = mode


def render_mode_toggle(prefix):
    """Dua tombol: 🖥️ Desktop | 📱 Mobile."""
    mode = st.session_state.view_mode
    m1, m2 = st.columns(2)
    with m1:
        st.button(
            "🖥️ Desktop", key=f"{prefix}_mode_desktop", width='stretch',
            type="primary" if mode == "Desktop" else "secondary",
            on_click=_set_mode, args=("Desktop",),
        )
    with m2:
        st.button(
            "📱 Mobile", key=f"{prefix}_mode_mobile", width='stretch',
            type="primary" if mode == "Mobile" else "secondary",
            on_click=_set_mode, args=("Mobile",),
        )


def _set_app_mode(mode):
    st.session_state.app_mode = mode


def render_app_mode_toggle(prefix):
    """Dua tombol: ⚡ Basic | 🛠️ Pro — menentukan berapa banyak pengaturan
    yang ditampilkan di Routing Optimizer (lihat IS_PRO)."""
    mode = st.session_state.app_mode
    m1, m2 = st.columns(2)
    with m1:
        st.button(
            "⚡ Basic", key=f"{prefix}_appmode_simple", width='stretch',
            type="primary" if mode == "Basic" else "secondary",
            on_click=_set_app_mode, args=("Basic",),
            help="Upload data, atur jumlah rute, klik buat rute — pengaturan lain pakai default yang masuk akal.",
        )
    with m2:
        st.button(
            "🛠️ Pro", key=f"{prefix}_appmode_pro", width='stretch',
            type="primary" if mode == "Pro" else "secondary",
            on_click=_set_app_mode, args=("Pro",),
            help="Semua pengaturan: pembagian petugas & hari kerja, prioritas, jam operasional, nama petugas, urutan manual, PDF, simpan sesi, dll.",
        )


def render_nav(prefix, horizontal=False):
    # Plain buttons (not a key-bound widget) so the active page can be set
    # programmatically from anywhere without hitting Streamlit's restriction
    # on mutating a widget's own session-state key after it's been created.
    pages = [
        ("Routing", "🛣️ Routing" if horizontal else "🛣️  Routing Optimizer", "routing"),
        ("Extract", "📍 Extractor" if horizontal else "📍  Maps Extractor", "extract"),
        ("Kobo", "📋 Survey" if horizontal else "📋  Survey Form", "kobo"),
    ]
    holders = st.columns(len(pages)) if horizontal else [st.container() for _ in pages]
    clicked = None
    for (page, label, k), holder in zip(pages, holders):
        with holder:
            if st.button(label, key=f"{prefix}_nav_{k}", width='stretch',
                         type="primary" if st.session_state.page == page else "secondary"):
                clicked = page
    if clicked:
        st.session_state.page = clicked
        st.rerun()


def render_howto():
    # Selalu tertutup saat pertama dibuka — pengguna bisa membukanya sendiri kalau perlu.
    with st.expander("ℹ️ Cara Pakai", expanded=False):
        t_quick, t_mode, t_field, t_survey, t_more = st.tabs(
            ["🚀 Mulai cepat", "⚡ Basic vs 🛠️ Pro", "📱 Di lapangan", "📋 Survey Form", "💡 Fitur & tips"]
        )
        with t_quick:
            st.markdown(
                "**1. Kumpulkan data** 📍  \n"
                "Upload Excel/CSV di **Routing Optimizer**, **tempel link Google Sheet** (kotak di sebelahnya), atau "
                "kumpulkan lewat **Maps Extractor** (link Google Maps, cari nama merchant, atau isi manual). "
                "Mau coba dulu? Klik **🧪 Coba dengan data contoh**.\n\n"
                "**2. Atur rute** 🛣️  \n"
                "Pilih cara menentukan jumlah rute (maksimal titik per rute, atau jumlah rute — mis. jumlah sales). "
                "**Titik awal**: isi titik awal (gudang, kantor, dll.) agar urutan rute dihitung darinya. Centang **🧭 Di lapangan, "
                "mulai navigasi Google Maps dari lokasi petugas** (bawaannya sudah tercentang; hilangkan centang bila navigasi harus mulai dari titik awal): "
                "urutan tetap, tapi link Google Maps dimulai dari posisi GPS petugas. Lalu klik **Buat Rute Optimal Sekarang**.\n\n"
                "**3. Pakai hasilnya** 📥  \n"
                "Pilih tampilan: **Detail rute**, **Peta semua rute**, **📱 Mode Lapangan**, atau **Ringkasan & perbandingan** "
                "(sebelum vs sesudah optimasi). Buka di Google Maps, kirim ke WhatsApp, salin teks rute, atau unduh Excel."
            )
        with t_mode:
            st.markdown(
                "Ganti kapan saja lewat tombol **Mode fitur** — data yang sudah diisi tidak hilang.\n\n"
                "- **⚡ Basic** — paling ringkas: upload data → atur jumlah rute → buat rute. Rute dimulai 08:00, "
                "tanpa durasi kunjungan, satu arah, dibagi otomatis per area. Titik awal boleh diisi (opsional).\n"
                "- **🛠️ Pro** — semua pengaturan lanjutan: jam mulai & durasi kunjungan, pulang-pergi, prioritas, jam "
                "operasional, pembagian petugas & hari kerja, pembagian \"isi penuh\", seimbangkan beban waktu, nama petugas, urutan manual, "
                "PDF, simpan sesi, dan preset."
            )
        with t_field:
            st.markdown(
                "**📱 Mode Lapangan** — tampilan sederhana untuk petugas: satu titik per layar dengan tombol navigasi besar, "
                "**Selesai / Lewati**, dan progres (selesai, dilewati, tersisa). Pilih di **Tampilan hasil** setelah rute dibuat.\n\n"
                "**🧭 Navigasi Google Maps** — tiap rute punya tombol navigasi (dibagi per bagian bila titiknya banyak). "
                "Kalau navigasi berhenti di titik singgah (\"sudah sampai tujuan\"), pakai **🧭 Navigasi titik demi titik "
                "(cadangan)**: tiap tombol memulai navigasi ke satu titik, lalu **⏭️ Titik berikutnya**. Rute bisa dikirim ke "
                "**WhatsApp** atau disalin sebagai teks.\n\n"
                "**🧭 Mulai dari lokasi petugas** — bila dicentang, urutan rute tetap dihitung dari titik awal yang Anda isi, "
                "tetapi link Google Maps dimulai dari posisi GPS petugas saat dibuka.\n\n"
                "**📋 Catat hasil kunjungan** — lewat formulir KoboCollect (tab **Survey Form**), bukan di rute."
            )
        with t_survey:
            st.markdown(
                "Menu **📋 Survey Form** menghubungkan rute dengan pencatatan kunjungan lewat KoboToolbox/KoboCollect.\n\n"
                "**1. Buat formulir** — di panel **Belum punya formulir? Buat dulu**: aplikasi membuat file XLSForm dari data "
                "merchant (setelah edit tabel). Petugas memilih nama merchant dari daftar (ID tersimpan otomatis), mengisi hasil "
                "kunjungan, lokasi GPS, dan foto lewat kamera. Isi nama petugas (satu per baris) bila mau jadi pilihan. "
                "Unggah file ke KoboToolbox → **Deploy**.\n\n"
                "**2. Petugas mengisi** — di aplikasi **KoboCollect** (bisa tanpa sinyal, dikirim saat ada internet).\n\n"
                "**3. Lihat hasil** — di panel **Hasil kunjungan**: tekan **Ambil hasil kunjungan terbaru**. Tabel memuat waktu, "
                "petugas, merchant, hasil, jarak dari titik merchant, tautan lokasi dan foto.\n\n"
                "**4. Perbarui Sheet** — bila data berasal dari Google Sheet dan penulisan balik sudah diatur, tombol "
                "**Perbarui kolom status di Google Sheet** menulis status baru (mis. *sudah akuisisi*, *tidak ditemukan*) "
                "sehingga merchant itu tidak ikut rute berikutnya.\n\n"
                "Pengaturan (token Kobo, penulisan ke Sheet) ada di **Secrets**; lihat SETUP_KOBO.md dan SETUP_SHEET_WRITE.md."
            )
        with t_more:
            st.markdown(
                "🔗 **Google Sheet:** tempel link di kotak sebelah upload, lalu **Ambil data dari Sheet**. Nyalakan "
                "**🔄 Perbarui otomatis** agar perubahan di Sheet masuk sendiri tiap 30 detik (ditahan bila kamu punya edit "
                "tabel di data itu). Link tersimpan di sesi. Bila penulisan balik diatur, **📤 Kirim hasil edit ke Google "
                "Sheet** menulis perubahan tabel ke Sheet (baris dikenali lewat kolom `merchant_id`).\n\n"
                "📍 **Koordinat kosong?** Biarkan kolom `latitude`/`longitude` kosong (atau tambah kolom `alamat`) — "
                "app menawarkan pencarian otomatis lewat OpenStreetMap, hasilnya bisa dicek dulu.\n\n"
                "✏️ **Data salah?** Buka **Lihat & Edit Data Awal** untuk memperbaiki sel atau menghapus baris, lalu "
                "unduh hasil editnya sebagai Excel. Titik yang melenceng jauh otomatis ditandai merah di pratinjau peta.\n\n"
                "📉 **Sebelum vs sesudah:** hasil rute dibandingkan dengan urutan merchant di file kamu, jadi kelihatan "
                "berapa km yang dihemat.\n\n"
                "🏷️ **Status merchant:** *prospek* (default), *sedang pendekatan*, *sudah akuisisi*, *belum tertarik*, *tidak ditemukan*. "
                "Dua status terakhir **tidak dimasukkan ke rute**. Ubah di **Lihat & Edit Data Awal** atau klik titik di "
                "**Pratinjau peta**.\n\n"
                "⭐ **Khusus Mode Pro:**\n"
                "- **Prioritas** — centang **⭐ prioritas** di **Lihat & Edit Data Awal** (atau kolom `prioritas` ya/tidak "
                "di Excel/CSV); merchant itu dikunjungi lebih dulu di rutenya.\n"
                "- **Jam operasional** — isi `jam_buka`/`jam_tutup` (HH:MM) di Excel/CSV atau di **Lihat & Edit Data Awal**. "
                "Jam tiba yang lewat jam tutup ditandai ⚠️. Ceklis **Optimalkan rute berdasarkan jam operasional** di "
                "Langkah 2 mengatur urutan: yang tutup lebih awal didahulukan, yang belum buka ditunda (atau petugas menunggu ⏳).\n"
                "- **Pembagian petugas & hari kerja** — centang di Langkah 2 untuk membagi merchant ke beberapa petugas "
                "(tiap petugas satu wilayah dan titik awalnya sendiri, mis. rumah petugas) dan ke hari kerja. Atur jumlah petugas, "
                "nama dan titik awal tiap petugas, dan maks. merchant per hari. **Hari kerja, Mulai tanggal, dan Sampai tanggal opsional**: "
                "kalau semuanya dikosongkan, hasil rute tidak menampilkan tanggal/hari (hanya petugas); kalau diisi, hasilnya jadwal "
                "petugas × tanggal. Untuk membatasi ke minggu tertentu (mis. hanya Senin–Selasa), pilih hari kerja Senin & Selasa, "
                "isi Mulai tanggal = Senin itu dan Sampai tanggal = Selasa itu; aplikasi memberi peringatan bila hari yang tersedia "
                "tidak cukup. Untuk satu hari dengan beberapa petugas, isi maks. merchant per hari yang cukup besar. "
                "**Kunci wilayah** menjaga petugas tetap di areanya. Selama mode ini aktif, **Pembagian rute** dan **Titik awal** "
                "biasa dinonaktifkan (titik awal diisi per petugas).\n"
                "- **Merchant terdekat** — di bagian **Titik awal**, centang **🎯 Ambil hanya merchant terdekat dari titik awal** "
                "dan isi jumlahnya (mis. 20 dari 70): hanya merchant terdekat (garis lurus) yang dibuatkan rute. Titik awal wajib diisi (di Pembagian petugas & "
                "hari kerja: titik awal minimal satu petugas).\n"
                "- **Seimbangkan beban waktu** — durasi tiap rute dibuat lebih mirip.\n"
                "- **Nama petugas** — isi di tiap rute setelah dibuat; ikut ke Excel, WhatsApp, dan PDF.\n"
                "- **Preset** — simpan kombinasi pengaturan bernama, mis. “Rute Pagi Sales”.\n\n"
                "💾 **Tips:** data tetap ada walau pindah menu. Bila simpan otomatis aktif, status **☁️ Tersimpan otomatis** "
                "tampil dan setelah refresh muncul tawaran **pulihkan sesi** (data, pengaturan, dan link Sheet). Tanpa itu, "
                "pakai **Simpan / Buka Sesi** (Mode Pro) atau unduh data hasil edit.\n\n"
                "🔒 **Login:** keluar otomatis bila 30 menit tidak digunakan; 2 menit sebelumnya muncul hitung mundur "
                "**Masih menggunakan halaman ini?** — tekan **Ya, masih** untuk melanjutkan."
            )


def render_mode_desc():
    st.caption(
        "🛠️ Semua pengaturan lanjutan aktif." if IS_PRO
        else "⚡ Tampilan ringkas — butuh pengaturan lanjutan? Pilih Pro."
    )


if IS_MOBILE:
    # Di HP sidebar disembunyikan (susah dibuka) — navigasi & mode pindah ke atas halaman.
    render_user_bar("top", compact=True)
    _persist_slot = st.empty()          # status simpan otomatis (diisi setelah autosave)
    with st.container(key="navrow"):
        render_nav("top", horizontal=True)
    st.caption("Mode fitur")
    render_app_mode_toggle("top")
    render_mode_desc()
    render_howto()
    if IS_PRO:
        render_session_panel("top")
    with st.expander("⚙️ Tampilan layar", expanded=False):
        with st.container(key="moderow"):
            render_mode_toggle("top")
    render_persist_diag()
else:
    with st.sidebar:
        st.markdown(
            DEV_BADGE_HTML + """
            <div class="sidebar-brand">
                <span class="emoji">⚡</span>
                <div>
                    <div class="title">Routing &amp; Extractor</div>
                    <div class="subtitle">Rute otomatis, lebih singkat & rapi</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        render_nav("side")
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        st.caption("Mode fitur")
        render_app_mode_toggle("side")
        render_mode_desc()
        render_howto()
        if IS_PRO:
            render_session_panel("side")
        with st.expander("⚙️ Tampilan layar", expanded=False):
            render_mode_toggle("side")
        _persist_slot = st.empty()      # status simpan otomatis (diisi setelah autosave)
        render_persist_diag()
        render_user_bar("side")


init_persistence()
autosave_session()      # keadaan akhir interaksi sebelumnya (juga bila run sebelumnya berhenti lebih awal lewat st.stop)
render_persist_caption(_persist_slot)
render_restore_offer()
_notice_slot = st.empty()
render_unsaved_notice(_notice_slot, IS_PRO)


# ================================================================
# HALAMAN 1: ROUTING PIPELINE OPTIMIZER
# ================================================================
IDLE_WARN_CSS = """<style>
.st-key-idlewarn{position:fixed;top:12px;left:50%;transform:translateX(-50%);z-index:1000000;
width:min(92vw,420px);background:#FFFBEB;color:#78350F;border:1px solid #F59E0B;border-radius:14px;
padding:14px 16px;box-shadow:0 10px 30px rgba(0,0,0,.25)}
.st-key-idlewarn p{color:#78350F;margin:0 0 .5rem 0}
</style>"""


def _idle_watch():
    """Dijalankan tiap detik (fragment, tidak menyegarkan waktu pakai). Menampilkan hitung mundur sebelum login berakhir."""
    ss = st.session_state
    tok = ss.get("auth_token")
    if not ss.get("auth_ok") or not tok:
        return
    rem = auth_session_remaining(tok, time.time())
    if rem is None or rem <= 0:
        st.rerun(scope="app")        # skrip utama memeriksa ulang dan menampilkan layar login
        return
    if rem > AUTH_WARN_SECONDS:
        return
    st.markdown(IDLE_WARN_CSS, unsafe_allow_html=True)
    with st.container(key="idlewarn"):
        _m, _s = divmod(int(rem), 60)
        st.markdown(f"**⏳ Sesi berakhir dalam {_m}:{_s:02d}**  \nMasih menggunakan halaman ini?")
        _c1, _c2 = st.columns(2)
        _stay = _c1.button("✅ Ya, masih", key="idle_stay", type="primary", width="stretch")
        _out = _c2.button("🚪 Keluar", key="idle_out", width="stretch")
    if _stay:
        auth_touch(ss)
        st.rerun(scope="fragment")
    if _out:
        _logout()
        st.rerun(scope="app")


def merged_edited_data(ss):
    """Data merchant gabungan (file + Maps Extractor) setelah edit tabel diterapkan, tanpa tampilan apa pun.
    Dipakai halaman Kunjungan. Return DataFrame atau None bila belum ada data valid."""
    parts = []
    for fname, fbytes in ss.uploaded_store.items():
        try:
            fd = read_table_file(fname, fbytes)
        except Exception:
            continue
        ok, _ = validate_dataframe(fd)
        if not ok:
            continue
        fd = fd.copy()
        fd["source_file"] = fname
        fd["_row_key"] = [f"{fname}#{i}" for i in range(len(fd))]
        parts.append(fd)
    if ss.get("use_extracted_flag") and ss.get("extracted_data"):
        ed = pd.DataFrame(ss.extracted_data)
        ok, _ = validate_dataframe(ed)
        if ok:
            ed = ed.copy()
            ed["source_file"] = "Data Ekstraksi (Maps Extractor)"
            ed["_row_key"] = [f"extract#{i}" for i in range(len(ed))]
            parts.append(ed)
    if not parts:
        return None
    d = ensure_status_column(pd.concat(parts, ignore_index=True))
    d = apply_data_edits(d, ss.data_edits)
    if d.empty:
        return None
    d = ensure_status_column(d)
    if not IS_PRO:
        d = d.drop(columns=[c for c in PRO_ONLY_COLS if c in d.columns])
    return d


def render_kobo_page():
    df = merged_edited_data(st.session_state)
    if df is None:
        st.info("Belum ada data merchant. Upload file atau ambil dari Google Sheet di halaman **Routing Optimizer** dulu; "
                "formulir KoboCollect dibuat dari data itu (termasuk edit tabelnya).")
    else:
        st.caption(f"Data yang dipakai: {len(df)} baris dari halaman Routing Optimizer (setelah edit tabel).")
        with st.expander("📝 Belum punya formulir KoboCollect (XLSForm)? Buat dulu", expanded=False):
            st.markdown("**Cukup sekali.** Aplikasi menyiapkan formulir kunjungan dari data merchant Anda, tinggal diunggah ke KoboToolbox.")
            st.caption("① Atur pilihan di bawah  →  ② Buat & download file  →  ③ Unggah di KoboToolbox lalu **Deploy**")
            st.caption(
                "Isi formulir: nama petugas, nama merchant (dipilih dari daftar, ID tersimpan otomatis), hasil kunjungan "
                "(sudah akuisisi, penjadwalan ulang, belum bertemu PIC, merchant tidak ditemukan, belum tertarik, sudah memiliki produk), "
                "lokasi GPS, dan foto lewat kamera."
            )
            _xf_title = st.text_input("Judul formulir", value="Kunjungan Merchant", key="xlsform_title", max_chars=80)
            _xf_has_p = any(str(c).strip().lower() == "petugas" for c in df.columns)
            _xf_filter = st.checkbox(
                "Petugas hanya melihat merchant miliknya", value=True, key="xlsform_filter", disabled=not _xf_has_p,
                help="Memakai kolom petugas di data (Mode Pro). Merchant tanpa petugas muncul untuk semua. "
                     "Tanpa kolom petugas, nama petugas diisi sendiri dan semua merchant muncul.",
            )
            _xf_extra = st.text_area(
                "Nama petugas (opsional, satu nama per baris)", key="xlsform_petugas", height=100,
                placeholder="Petugas 1\nPetugas 2",
                help="Dipakai sebagai pilihan nama petugas di formulir, ditambah petugas yang sudah ada di kolom petugas data. "
                     "Kosongkan semuanya kalau petugas mau mengetik namanya sendiri.",
            )
            _xf_extra_list = [x.strip() for x in _xf_extra.splitlines() if x.strip()][:200]
            _xf_all = st.checkbox("Sertakan merchant berstatus 'sudah akuisisi' / 'belum tertarik' / 'tidak ditemukan'", value=False, key="xlsform_all")
            if st.button("🛠️ Buat formulir", key="xlsform_btn", width="stretch"):
                try:
                    _xb, _xi = build_xlsform(df, _xf_title.strip() or "Kunjungan Merchant", _xf_filter, _xf_all, _xf_extra_list)
                    st.session_state.xlsform_out = (_xb, _xi)
                except Exception as e:
                    st.session_state.xlsform_out = None
                    st.error(f"Gagal membuat formulir: {e}")
            _xo = st.session_state.get("xlsform_out")
            if _xo:
                _xb, _xi = _xo
                st.success(f"Formulir siap: {_xi['merchants']} merchant"
                           + (f", {_xi['petugas']} petugas (pilihan{', merchant difilter per petugas' if _xi['filtered'] else ''})"
                              if _xi["petugas"] else ", nama petugas diisi sendiri"))
                for _w in _xi["warnings"]:
                    st.warning(_w)
                st.download_button("⬇️ Download formulir (XLSForm .xlsx)", data=_xb, file_name="form_kunjungan_merchant.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="xlsform_dl",
                                   type="primary", width="stretch")
                st.caption("Di KoboToolbox: **New → Upload an XLSForm** → pilih file ini → **Deploy**. Kalau data merchant berubah, buat formulir lagi "
                           "dan **Redeploy** (atau unggah sebagai versi baru).")

    _kcfg = kobo_config()
    with st.container(border=True):
        st.markdown("#### 📋 Hasil kunjungan (KoboToolbox)")
        if not _kcfg:
            st.caption("Belum diatur. Isi KOBO_TOKEN dan KOBO_ASSET_UID (dan KOBO_SERVER bila bukan server global) di secrets; "
                       "lihat SETUP_KOBO.md bagian API.")
        else:
            st.caption("Mengambil isian formulir kunjungan langsung dari KoboToolbox. Satu merchant memakai kunjungan terbarunya.")
            if st.button("🔄 Ambil hasil kunjungan terbaru", key="kobo_fetch_btn", width="stretch"):
                with st.spinner("Mengambil dari KoboToolbox…"):
                    _kok, _kres = kobo_fetch(_kcfg)
                if _kok:
                    st.session_state.kobo_latest = kobo_latest(_kres)
                    st.session_state.kobo_labels = kobo_choice_labels(_kcfg)
                    st.session_state.kobo_total = len(_kres)
                    st.session_state.kobo_time = time.time()
                else:
                    st.error(_kres)
            _kl = st.session_state.get("kobo_latest")
            if _kl is not None:
                st.caption(f"{st.session_state.get('kobo_total', 0)} isian · {len(_kl)} merchant · "
                           f"diambil {_ago(datetime.datetime.fromtimestamp(st.session_state.kobo_time, datetime.timezone.utc).isoformat())}")
                if len(_kl):
                    st.dataframe(
                        kobo_view(_kl, df, st.session_state.get("kobo_labels")), width="stretch", hide_index=True,
                        column_config={
                            "Jarak dari titik (m)": st.column_config.NumberColumn(format="%d"),
                            "Lokasi": st.column_config.LinkColumn(display_text="📍 Buka"),
                            "Foto": st.column_config.LinkColumn(display_text="🖼️ Lihat"),
                        },
                    )
                    st.caption("Jarak besar dari titik merchant bisa berarti kunjungan tidak dilakukan di lokasi. "
                               "Foto terbuka bila Anda sedang login di KoboToolbox.")
                    _syk, _wc = st.session_state.get("sheet_sync"), sheet_write_config()
                    if _syk and _wc:
                        if st.button("📤 Perbarui kolom status di Google Sheet dari hasil kunjungan", key="kobo_to_sheet_btn", width="stretch",
                                     help="Mengubah kolom status di Sheet sesuai pilihan petugas (status_baru). Merchant 'sudah akuisisi' "
                                          "dan 'belum tertarik' otomatis tidak diikutkan ke rute berikutnya; begitu juga merchant 'tidak ditemukan'."):
                            try:
                                _sdf = read_table_file(_syk["fname"], st.session_state.uploaded_store[_syk["fname"]])
                                _upd, _ndf, _unk = kobo_status_updates(_kl, _sdf)
                            except Exception as e:
                                _upd, _ndf, _unk = [], None, 0
                                st.error(f"Gagal menyiapkan data: {e}")
                            if _upd:
                                _wok, _wres = sheet_write_post(_wc, _upd)
                                if _wok:
                                    sheet_sync_apply(st.session_state, _ndf.to_csv(index=False).encode("utf-8"), time.time(), drop_edits=False)
                                    st.session_state._sheet_flash = (f"✅ Status {_wres.get('updated', 0)} merchant diperbarui di Google Sheet."
                                                                     + (f" {_unk} ID dari Kobo tidak ada di Sheet." if _unk else ""))
                                    st.rerun(scope="app")
                                else:
                                    st.error(_wres)
                            elif _ndf is not None:
                                st.info("Semua status di Sheet sudah sama dengan hasil kunjungan.")
                    else:
                        st.caption("Untuk memperbarui status di Sheet: ambil data dari link Google Sheet dan atur SHEET_WRITE_URL/SHEET_WRITE_SECRET.")




st.fragment(run_every=1)(_idle_watch)()

if st.session_state.page == "Routing":
    render_hero(
        "Optimasi rute", "Routing Pipeline", "Optimizer",
        "Optimalkan rute kunjungan dengan clustering (KMeans) dan penentuan urutan kunjungan (TSP) yang diselesaikan dengan Google OR-Tools.",
    )

    stepper_slot = st.empty()
    render_stepper(stepper_slot, 0)

    section_header(
        "1️⃣", "Siapkan Data Merchant",
        "Upload file Excel/CSV, ambil dari link Google Sheet, pakai data dari Maps Extractor, atau gabungan semuanya",
    )

    _c_up, _c_sheet = st.columns(2, gap="medium")   # di HP otomatis tersusun ke bawah
    with _c_up:
        new_files = st.file_uploader(
            "📂 Upload Data (Excel / CSV)",
            type=["xlsx", "csv"],
            accept_multiple_files=True,
            key=f"uploader_{st.session_state.uploader_nonce}",
            help="Format .xlsx atau .csv. Kolom wajib: merchant_name, latitude, longitude (koma desimal seperti -7,56 juga dikenali). latitude/longitude boleh dikosongkan — akan dicari otomatis dari nama merchant (tambah kolom alamat supaya lebih akurat). Kolom opsional: status (prospek / sedang pendekatan / sudah akuisisi / belum tertarik / tidak ditemukan — tiga yang terakhir tidak diikutkan ke rute; kosong = prospek), prioritas (ya/tidak — dikunjungi lebih dulu) serta jam_buka & jam_tutup (HH:MM — dicek terhadap perkiraan jam tiba); dua kolom terakhir ini hanya dipakai di Mode Pro. Bisa pilih beberapa file sekaligus — nanti otomatis digabung. File yang sudah diupload tetap tersimpan walau kamu pindah ke Maps Extractor.",
        )
    with _c_sheet:
        _sheet_link = st.text_input(
            "🔗 Atau ambil dari link Google Sheet", key=f"sheet_link_input_{st.session_state.widget_nonce}",
            value=st.session_state.sheet_link_saved,
            placeholder="https://docs.google.com/spreadsheets/d/…/edit#gid=0",
            help=("Isi tab Sheet dibaca seperti file CSV: kolom sama dengan file upload (merchant_name, latitude, longitude, dst.). "
                  "Sheet harus dibagikan sebagai **Siapa saja yang memiliki link → Pelihat**; artinya siapa pun yang tahu linknya "
                  "bisa membuka datanya, jadi jangan dipakai untuk data sensitif (unduh sebagai CSV lalu upload saja). "
                  "Untuk tab tertentu, buka tab itu lalu salin link (mengandung #gid=…). Ambil lagi dengan link yang sama untuk "
                  "memperbarui data."),
        )
        _sheet_go = st.button("📥 Ambil data dari Sheet", key="sheet_fetch_btn", width='stretch')
        _sy = st.session_state.get("sheet_sync")
        if _sy:
            def _sync_toggle():
                if st.session_state.get("sheet_sync"):
                    st.session_state.sheet_sync["on"] = bool(st.session_state.get(f"sheet_sync_toggle_{st.session_state.widget_nonce}"))
            st.toggle(
                f"🔄 Perbarui otomatis (tiap {SHEET_SYNC_SECONDS} detik)", value=bool(_sy["on"]), key=f"sheet_sync_toggle_{st.session_state.widget_nonce}",
                on_change=_sync_toggle,
                help="Selama halaman ini terbuka, aplikasi mengecek Sheet secara berkala dan memuat perubahannya ke tabel "
                     "Lihat & Edit Data Awal. Google kadang menunda beberapa detik sampai menit sebelum perubahan terbaca. "
                     "Pembaruan ditahan kalau Anda punya edit tabel pada data Sheet ini, supaya edit tidak menimpa atau salah sasaran.",
            )

            def _sheet_sync_tick():
                ss = st.session_state
                _stt = sheet_sync_check(ss, time.time())
                if _stt == "applied":
                    st.toast("🔄 Data dari Google Sheet diperbarui")
                    st.rerun(scope="app")
                sy = ss.get("sheet_sync")
                if not sy:
                    return
                _utc = datetime.timezone.utc
                if sy.get("checked"):
                    _txt = f"Dicek {_ago(datetime.datetime.fromtimestamp(sy['checked'], _utc).isoformat())}"
                    if sy.get("changed"):
                        _txt += f" · terakhir berubah {_ago(datetime.datetime.fromtimestamp(sy['changed'], _utc).isoformat())}"
                    st.caption("🔄 " + _txt)
                if sy.get("error"):
                    st.caption(f"⚠️ Gagal memeriksa Sheet: {sy['error']} Akan dicoba lagi.")
                pend = sy.get("pending")
                if pend:
                    if pend[1] == "edits":
                        st.warning("Sheet berubah, tetapi Anda punya edit tabel pada data Sheet ini, jadi belum dimuat.")
                        if st.button("Terapkan data Sheet (edit tabel pada Sheet ini dihapus)", key="sheet_apply_force", width='stretch'):
                            sheet_sync_apply(ss, pend[0], time.time(), drop_edits=True)
                            st.rerun(scope="app")
                    else:
                        st.info("Sheet berubah. Terapkan atau batalkan perubahan di tabel dulu; data Sheet dimuat otomatis setelahnya.")

            st.fragment(run_every=SHEET_SYNC_SECONDS if _sy["on"] else None)(_sheet_sync_tick)()
    if new_files:
        for nf in new_files:
            st.session_state.uploaded_store[nf.name] = nf.getvalue()
        st.session_state.uploader_nonce += 1
        st.rerun()

    _sheet_flash = st.session_state.pop("_sheet_flash", None)
    if _sheet_flash:
        st.success(_sheet_flash)
    if _sheet_go:
        if not _sheet_link.strip():
            st.error("Tempel link Google Sheet dulu.")
        else:
            with st.spinner("Mengambil data dari Google Sheets…"):
                _ok, _res, _fname = fetch_google_sheet_csv(_sheet_link)
            if _ok:
                sheet_sync_start(st.session_state, _sheet_link, _fname, _res)
                st.session_state.data_edit_nonce = st.session_state.get("data_edit_nonce", 0) + 1
                st.session_state._sheet_flash = f"✅ Data dari Google Sheet dimuat sebagai **{_fname}**."
                st.rerun()
            else:
                st.error(_res)


    # Daftar file yang tersimpan (tetap ada setelah pindah halaman)
    if st.session_state.uploaded_store:
        st.caption(f"📎 {len(st.session_state.uploaded_store)} file tersimpan")
        for i, fname in enumerate(list(st.session_state.uploaded_store.keys())):
            with st.container(key=f"filerow_{i}"):
                fc1, fc2 = st.columns([6, 1])
                with fc1:
                    st.markdown(f"📄 `{fname}`")
                with fc2:
                    if st.button("✖", key=f"rm_{fname}", help=f"Hapus {fname}"):
                        st.session_state.uploaded_store.pop(fname, None)
                        st.rerun()

    if not st.session_state.uploaded_store and not st.session_state.extracted_data:
        if st.button("🧪 Coba dengan data contoh (12 merchant)", width='stretch',
                     help="Memuat 12 merchant fiktif di sekitar Surakarta supaya kamu bisa langsung mencoba. Bisa dihapus kapan saja dengan tombol ✖."):
            st.session_state.uploaded_store["data_contoh.csv"] = make_sample_csv()
            st.rerun()

    use_extracted = False
    if st.session_state.extracted_data:
        use_extracted = st.checkbox(
            f"📋 Pakai {len(st.session_state.extracted_data)} data dari Maps Extractor",
            value=st.session_state.use_extracted_flag,
            key=_wk("_use_extracted_widget"),
            on_change=_sync_use_extracted,
            help="Bisa dicentang bersamaan dengan upload Excel di atas — keduanya akan digabung otomatis.",
        )
    else:
        st.session_state.use_extracted_flag = False

    with st.expander("📄 Belum punya file? Unduh template", expanded=False):
        tpl1, tpl2 = st.columns(2)
        with tpl1:
            st.download_button(
                "⬇️ Template Excel",
                data=make_template_excel(),
                file_name="template_routing.xlsx",
                mime="application/vnd.ms-excel",
                help="Belum punya file? Download contoh formatnya di sini supaya langsung cocok.",
                width='stretch',
            )
        with tpl2:
            st.download_button(
                "⬇️ Template CSV",
                data=make_template_csv(),
                file_name="template_routing.csv",
                mime="text/csv",
                help="Contoh format CSV (kolom: merchant_name, latitude, longitude).",
                width='stretch',
            )

    df = None
    valid_parts = []
    file_errors = []

    for fname, fbytes in st.session_state.uploaded_store.items():
        try:
            file_df = read_table_file(fname, fbytes)
        except Exception as e:
            file_errors.append(f"**{fname}**: gagal dibaca ({e})")
            continue

        is_valid, errors = validate_dataframe(file_df)
        if not is_valid:
            for err in errors:
                file_errors.append(f"**{fname}**: {err}")
            continue

        file_df = file_df.copy()
        file_df["source_file"] = fname
        file_df["_row_key"] = [f"{fname}#{i}" for i in range(len(file_df))]  # kunci stabil untuk edit tabel
        valid_parts.append(file_df)

    if use_extracted:
        extracted_df = pd.DataFrame(st.session_state.extracted_data)
        is_valid, errors = validate_dataframe(extracted_df)
        if not is_valid:
            for err in errors:
                file_errors.append(f"**Data Ekstraksi (Maps Extractor)**: {err}")
        else:
            extracted_df = extracted_df.copy()
            extracted_df["source_file"] = "Data Ekstraksi (Maps Extractor)"
            extracted_df["_row_key"] = [f"extract#{i}" for i in range(len(extracted_df))]
            valid_parts.append(extracted_df)

    for err in file_errors:
        st.error(f"❌ {err}")

    if valid_parts:
        df = pd.concat(valid_parts, ignore_index=True)
        total_sources = len(st.session_state.uploaded_store) + (1 if use_extracted else 0)
        skipped = total_sources - len(valid_parts)
        msg = f"✅ {len(valid_parts)} sumber data berhasil digabung — total {len(df)} baris."
        if skipped:
            msg += f" ({skipped} sumber dilewati karena error di atas)"
        if len(valid_parts) > 1:
            st.success(msg)
    elif (st.session_state.uploaded_store or use_extracted) and not file_errors:
        # Shouldn't normally happen, but avoid silently doing nothing.
        st.info("Tidak ada data untuk diproses.")
    elif file_errors:
        st.stop()

    if df is not None:
        render_stepper(stepper_slot, 1)
        df = ensure_status_column(df)  # kolom status (default "prospek")
        df = apply_data_edits(df, st.session_state.data_edits)  # hapus/ubah baris dari tabel Data Awal
        if not df.empty:
            df = ensure_status_column(df)  # edit bisa mengisi status apa saja — samakan lagi ke nilai baku
        if df.empty:
            st.info("Semua baris sudah dihapus lewat tabel Data Awal. Batalkan edit atau upload data lagi.")
            if st.session_state.data_edits["deleted"] or st.session_state.data_edits["changed"]:
                if st.button("↩️ Batalkan semua edit tabel", key="_edits_reset_empty"):
                    st.session_state.data_edits = {"deleted": [], "changed": {}}
                    st.session_state.data_edit_nonce += 1
                    st.rerun()
            st.stop()
        _edited_full = df.copy()  # data setelah edit tabel, sebelum pencarian koordinat/dedupe (untuk download)
        _pro_ignored = [] if IS_PRO else pro_columns_with_data(df)   # untuk info di bawah (kolom di-drop sebentar lagi)
        if not IS_PRO:
            # Prioritas & jam operasional khusus Mode Pro: di Basic kolomnya diabaikan (tidak tampil, tidak dicek,
            # tidak dioptimasi). Isinya tidak hilang — tetap ada di file download dan muncul lagi di Pro.
            df = df.drop(columns=[c for c in PRO_ONLY_COLS if c in df.columns])
        _n_before_geo = len(df)
        df = handle_missing_coordinates(df)  # isi koordinat kosong lewat pencarian otomatis
        _n_nocoord = _n_before_geo - len(df)  # baris yang belum punya koordinat (belum ikut rute)
        df["latitude"] = pd.to_numeric(df["latitude"])
        df["longitude"] = pd.to_numeric(df["longitude"])
        _geo_filled = df[["_row_key", "latitude", "longitude"]].copy()

        # Deteksi duplikat (nama sama + koordinat sama ~1 meter), mis. setelah
        # menggabungkan Excel dengan data Maps Extractor.
        _dup_mask = pd.DataFrame(
            {
                "n": df["merchant_name"].astype(str).str.strip().str.lower(),
                "a": df["latitude"].round(5),
                "o": df["longitude"].round(5),
            }
        ).duplicated()
        n_dup = int(_dup_mask.sum())
        if n_dup:
            remove_dups = st.checkbox(
                f"🧹 Hapus {n_dup} baris duplikat (nama & koordinat sama)",
                value=st.session_state.dedupe_flag,
                key=_wk("_dedupe_widget"),
                on_change=_sync_dedupe,
                help="Baris pertama dipertahankan. Matikan kalau memang ada merchant kembar yang sengaja dimasukkan dua kali.",
            )
            if remove_dups:
                df = df[~_dup_mask].copy().reset_index(drop=True)

        if _pro_ignored:
            _ign_txt = ", ".join(f"{_lbl} ({_n} baris)" for _lbl, _n in _pro_ignored)
            st.info(
                f"🛠️ File ini punya kolom khusus Pro yang berisi data: **{_ign_txt}**. Di Mode Basic kolom itu "
                "**tidak dipakai** untuk membuat rute. Datanya tidak hilang dan tetap ada di file download.",
            )
            st.button("🛠️ Pindah ke Mode Pro", key="_ignored_cols_to_pro", on_click=_set_app_mode, args=("Pro",))

        _edits = st.session_state.data_edits
        _n_edits = len(_edits["deleted"]) + sum(len(c) for c in _edits["changed"].values())
        _n_hours = count_merchants_with_hours(df) if IS_PRO else 0
        _hours_opt_choice = False
        with st.expander(
            f"📄 Lihat & Edit Data Awal ({len(df)} baris)" + (f" · {_n_edits} edit" if _n_edits else ""),
            expanded=st.session_state.table_panel_open,
        ):
            st.caption(
                "✏️ Klik sel untuk memperbaiki nama, koordinat, atau **status**, atau centang **Hapus** untuk "
                "membuang baris. Tekan **Terapkan perubahan** supaya tersimpan — file aslinya tidak diubah. "
                "Status **sudah akuisisi**, **belum tertarik**, dan **tidak ditemukan** tidak diikutkan ke rute; **prospek** dan "
                "**sedang pendekatan** tetap diikutkan."
                + ("\n\n"
                   "🕒 Isi **jam_buka** & **jam_tutup** (format HH:MM, mis. 08:00 dan 21:00) untuk merchant yang punya "
                   "jam operasional. Dipakai untuk menandai ⚠️ kalau perkiraan jam tiba di luar jam buka, dan untuk "
                   "ceklis **Optimalkan rute berdasarkan jam operasional** yang muncul di bawah ini. Kosongkan kalau tidak diketahui."
                   if IS_PRO else "")
                + ("\n\n⭐ Centang **prioritas** untuk merchant yang harus dikunjungi lebih dulu di rutenya."
                   if IS_PRO else "")
            )
            _flash_h = st.session_state.pop("hours_flash", None)
            if _flash_h:
                st.warning(_flash_h)
            if IS_PRO and _n_hours:
                _hours_opt_choice = st.checkbox(
                    "🕒 Optimalkan rute berdasarkan jam operasional merchant",
                    value=bool(st.session_state.hours_opt_flag),
                    key=_wk("_hours_opt_widget"),
                    on_change=_sync_hours_opt,
                    help=(
                        "Urutan kunjungan di dalam tiap rute diatur supaya merchant didatangi saat sedang buka.\n\n"
                        "- Yang **tutup lebih awal** dikunjungi lebih dulu; yang **baru buka siang** belakangan.\n"
                        "- Kalau merchant **belum buka** saat rute dimulai, merchant lain dikunjungi dulu; kalau tidak "
                        "ada lagi, petugas menunggu sampai buka (ditandai ⏳).\n"
                        "- Merchant **tanpa jam** tidak dibatasi; rute tanpa jam sama sekali memakai KMeans + TSP biasa.\n"
                        "- Pembagian merchant ke rute tetap mengikuti area. Kalau semua jam tak mungkin dipenuhi, "
                        "dipilih urutan dengan pelanggaran paling sedikit.\n"
                        "- Pengaturan prioritas tidak dipakai di rute yang punya jam."
                    ),
                )
                st.caption(f"🕒 {_n_hours} dari {len(df)} merchant punya jam operasional.")
            _edit_cols = [c for c in EDITABLE_COLS if c in df.columns or (IS_PRO and c in PRO_ONLY_COLS)]
            _info_cols = [c for c in ("source_file", "koordinat_dari") if c in df.columns]
            _view = df.reindex(columns=["_row_key"] + _edit_cols + _info_cols).copy()
            for _tc in _edit_cols:  # kolom teks dibuat string murni supaya editor tidak error pada tipe campuran
                if _tc == "prioritas":   # kotak centang: kata seperti ya/yes/1/penting dianggap tercentang
                    _view[_tc] = _view[_tc].apply(is_truthy).astype(bool)
                elif _tc not in ("latitude", "longitude"):
                    _view[_tc] = _view[_tc].apply(lambda v: "" if pd.isna(v) else str(v))
            _view.insert(0, "hapus", False)
            @st.fragment
            def _data_edit_fragment(view, edit_cols, info_cols, editor_nonce):
                auth_touch(st.session_state)   # mengetik di tabel ini tidak menjalankan ulang halaman: tetap dihitung aktif
                # Fragment: mengetik di tabel hanya menjalankan ulang bagian ini (bukan seluruh halaman),
                # jadi jumlah perubahan yang belum diterapkan bisa ditampilkan langsung.
                # PENTING: semua data masuk lewat argumen. Pada rerun fragment skrip utama tidak dijalankan ulang,
                # jadi variabel global bernama sama (mis. _view di bagian hasil rute) bisa sudah berubah isinya.
                _edited = st.data_editor(
                    view,
                    key=f"data_editor_{editor_nonce}",
                    hide_index=True, num_rows="fixed", width="stretch",
                    disabled=["_row_key"] + info_cols,
                    column_config={
                        "_row_key": None,
                        "hapus": st.column_config.CheckboxColumn("🗑️ Hapus", default=False),
                        "latitude": st.column_config.NumberColumn("latitude", format="%.6f"),
                        "longitude": st.column_config.NumberColumn("longitude", format="%.6f"),
                        "status": st.column_config.SelectboxColumn(
                            "status", options=STATUS_OPTIONS, required=True, width="medium",
                        ),
                        "prioritas": st.column_config.CheckboxColumn(
                            "⭐ prioritas", default=False,
                            help="Centang kalau merchant ini harus dikunjungi lebih dulu di rutenya."),
                        "petugas": st.column_config.TextColumn(
                            "👤 petugas", max_chars=60,
                            help="Wilayah tetap: nama petugas yang memegang merchant ini. Dipakai di Rencana beberapa "
                                 "hari saat 'Kunci wilayah petugas' aktif; ubah di sini untuk memindahkan merchant antar petugas."),
                        "jam_buka": st.column_config.TextColumn(
                            "🕒 jam_buka", max_chars=8,
                            help="Jam buka, format HH:MM (mis. 08:00). Kosong = tidak dicek."),
                        "jam_tutup": st.column_config.TextColumn(
                            "🕒 jam_tutup", max_chars=8,
                            help="Jam tutup, format HH:MM (mis. 21:00). Buka lewat tengah malam: 18:00 → 02:00."),
                    },
                    **TABLE_KW,
                )
                _p_del, _p_chg = diff_data_edits(view, _edited, edit_cols)
                _n_pending = len(_p_del) + sum(len(c) for c in _p_chg.values())
                if _n_pending:
                    st.warning(
                        f"✏️ **{_n_pending} perubahan belum diterapkan.** Tekan **Terapkan perubahan** supaya "
                        "tersimpan — kalau tidak, perubahan ini hilang saat halaman dimuat ulang."
                    )
                _apply_edits = st.button(
                    "✅ Terapkan perubahan" + (f" ({_n_pending})" if _n_pending else ""),
                    key=f"data_edit_apply_{editor_nonce}", type="primary",
                )
                if _apply_edits:
                    _del, _chg = _p_del, _p_chg
                    _chg, _bad = normalize_hours_changes(_chg)
                    _chg = normalize_priority_changes(_chg)
                    _bad_msg = ""
                    if _bad:
                        _names = view.set_index("_row_key")["merchant_name"]
                        _bad_msg = (
                            "⚠️ Jam berikut bukan format HH:MM (mis. 08:00) dan tidak disimpan: "
                            + "; ".join(f"{_names.get(k, k)} → {c} = “{v}”" for k, c, v in _bad[:8])
                            + (f" (+{len(_bad) - 8} lagi)" if len(_bad) > 8 else "")
                        )
                    if _del or _chg:
                        _store = st.session_state.data_edits
                        _store["deleted"] = sorted(set(_store["deleted"]) | set(_del))
                        for _k, _cols in _chg.items():
                            _store["changed"].setdefault(_k, {}).update(_cols)
                        st.session_state.data_edit_nonce += 1
                        st.session_state.table_panel_open = True  # tetap terbuka setelah diterapkan
                        if _bad_msg:
                            st.session_state.hours_flash = _bad_msg
                        st.rerun(scope="app")   # data berubah -> seluruh halaman dihitung ulang
                    elif _bad_msg:
                        st.warning(_bad_msg)
                    else:
                        st.info("Belum ada perubahan untuk diterapkan.")

            _data_edit_fragment(_view, _edit_cols, _info_cols, st.session_state.data_edit_nonce)
            if _n_edits:
                _dl1, _dl2 = st.columns(2)
                with _dl1:
                    st.download_button(
                        f"⬇️ Download data hasil edit ({len(_edited_full)} baris, Excel)",
                        data=build_edited_data_excel(_edited_full, _geo_filled),
                        file_name="data_hasil_edit.xlsx", mime="application/vnd.ms-excel",
                        key="_edited_data_dl", type="primary", width="stretch",
                        help="Berisi semua baris setelah edit diterapkan (gabungan semua sumber data). Bisa langsung "
                             "diupload lagi, jadi tidak perlu mengedit ulang di lain waktu.",
                    )
                with _dl2:
                    if st.button("↩️ Batalkan semua edit tabel", key="_edits_reset", width="stretch"):
                        st.session_state.data_edits = {"deleted": [], "changed": {}}
                        st.session_state.data_edit_nonce += 1
                        st.rerun()
                st.caption(
                    "File download hanya memuat perubahan yang sudah **diterapkan** (bukan yang masih diketik di tabel)."
                )
            _sy_w = st.session_state.get("sheet_sync")
            if _sy_w and _n_edits:
                _wcfg = sheet_write_config()
                _pre_w = _sy_w["fname"] + "#"
                _n_w = sum(1 for k in _edits["changed"] if str(k).startswith(_pre_w))
                if _n_w:
                    if not _wcfg:
                        st.caption("📤 Kirim edit balik ke Google Sheet: belum diatur (isi SHEET_WRITE_URL dan SHEET_WRITE_SECRET di secrets; lihat SETUP_SHEET_WRITE.md).")
                    else:
                        _del_w = sum(1 for k in _edits["deleted"] if str(k).startswith(_pre_w))
                        if st.button(f"📤 Kirim {_n_w} baris hasil edit ke Google Sheet", key="sheet_write_btn", width="stretch",
                                     help="Menulis nilai yang Anda ubah ke baris yang sama di Sheet (dikenali lewat kolom merchant_id). "
                                          "Hanya kolom yang boleh ditulis di skrip Apps Script yang berubah. Baris yang dihapus di tabel "
                                          "tidak dihapus dari Sheet."):
                            try:
                                _upd, _newdf, _skip = sheet_write_build(_sy_w["fname"], st.session_state.uploaded_store[_sy_w["fname"]], _edits)
                            except Exception as e:
                                _upd, _newdf, _skip = [], None, 0
                                st.error(f"Gagal menyiapkan data: {e}")
                            if _upd:
                                with st.spinner("Mengirim ke Google Sheet…"):
                                    _wok, _wres = sheet_write_post(_wcfg, _upd)
                                if _wok:
                                    _wmiss = len(_wres.get("missing") or [])
                                    ss_w = st.session_state
                                    sheet_sync_apply(ss_w, _newdf.to_csv(index=False).encode("utf-8"), time.time(), drop_edits=True)
                                    ss_w._sheet_flash = (f"✅ {_wres.get('updated', 0)} baris ditulis ke Google Sheet."
                                                         + (f" {_wmiss} ID tidak ditemukan di Sheet." if _wmiss else "")
                                                         + (f" {_skip} baris dilewati karena tidak punya merchant_id." if _skip else ""))
                                    st.rerun(scope="app")
                                else:
                                    st.error(_wres)
                            elif _newdf is not None:
                                st.warning("Tidak ada baris dengan merchant_id yang bisa dikirim.")
                        if _del_w:
                            st.caption(f"ℹ️ {_del_w} baris yang Anda hapus di tabel tidak ikut dihapus dari Sheet.")

        # Pemeriksaan titik janggal + pratinjau peta semua titik.
        # Titik berstatus akuisisi/belum tertarik tidak akan dirutekan, jadi tidak ikut diperiksa.
        _outliers = detect_outlier_points(df[~df["status"].isin(STATUS_EXCLUDED)])
        if _outliers:
            st.warning(
                f"⚠️ **{len(_outliers)} titik tampak janggal** — jauh dari titik-titik lainnya, biasanya "
                "karena koordinat salah. Satu titik yang melenceng bisa membuat jarak rute melonjak. "
                "Perbaiki di tabel **Data Awal** di atas, atau keluarkan dari rute."
            )
            st.dataframe(
                pd.DataFrame({
                    "merchant_name": df.loc[list(_outliers), "merchant_name"].values,
                    "latitude": df.loc[list(_outliers), "latitude"].values,
                    "longitude": df.loc[list(_outliers), "longitude"].values,
                    "Alasan": list(_outliers.values()),
                }),
                width="stretch", hide_index=True,
            )
            _exclude_outliers = st.checkbox(
                "🚫 Jangan ikutkan titik janggal ini saat membuat rute",
                value=st.session_state.exclude_outliers_flag,
                key=_wk("_exclude_outliers_widget"),
                on_change=_sync_exclude_outliers,
            )
        else:
            _exclude_outliers = False
        _sel_key = st.session_state.map_selected_key
        _sel_rows = df.index[df["_row_key"] == _sel_key] if _sel_key is not None else []
        _sel_idx = _sel_rows[0] if len(_sel_rows) else None
        with st.expander(
            f"🗺️ Pratinjau peta semua titik ({len(df)})",
            expanded=bool(_outliers) or st.session_state.map_panel_open,
        ):
            _cnt = status_counts(df)
            st.caption(
                " · ".join(
                    f"{STATUS_EMOJI[k]} {k.capitalize()} {_cnt[k]}" + (" (tidak diikutkan)" if k in STATUS_EXCLUDED and _cnt[k] else "")
                    for k in STATUS_OPTIONS
                )
            )
            _show_labels = st.checkbox("🏷️ Tampilkan nama merchant di peta", value=True, key="_map_labels")
            _map_out = st_folium(
                build_preview_map(df, set(_outliers), show_labels=_show_labels),  # tanpa cincin pilihan: peta tidak digambar ulang tiap klik
                width=None, height=MAP_H, key="preview_map",
                returned_objects=["last_object_clicked", "last_object_clicked_tooltip"],
            )
            _click = _map_out.get("last_object_clicked") if isinstance(_map_out, dict) else None
            if _click:
                _sig = (
                    round(float(_click.get("lat", 0)), 7), round(float(_click.get("lng", 0)), 7),
                    str(_map_out.get("last_object_clicked_tooltip") or ""),
                )
                if _sig != st.session_state.map_last_click_sig:  # klik baru (bukan sisa klik lama)
                    st.session_state.map_last_click_sig = _sig
                    _hit = pick_clicked_index(df, _click, _map_out.get("last_object_clicked_tooltip"))
                    st.session_state.map_selected_key = df.at[_hit, "_row_key"] if _hit is not None else None
                    st.session_state.map_panel_open = True
                    _sel_key = st.session_state.map_selected_key
                    _sel_rows = df.index[df["_row_key"] == _sel_key] if _sel_key is not None else []
                    _sel_idx = _sel_rows[0] if len(_sel_rows) else None
            if _sel_idx is not None:
                _row = df.loc[_sel_idx]
                _cur = _row["status"]
                st.markdown(f"**📍 {_row['merchant_name']}** — status sekarang: {STATUS_EMOJI[_cur]} **{_cur}**")
                _mc1, _mc2, _mc3 = st.columns([2, 1, 1])
                with _mc1:
                    st.selectbox(
                        "Ubah status", STATUS_OPTIONS, index=STATUS_OPTIONS.index(_cur),
                        key=f"_map_status_{_sel_key}",
                    )
                with _mc2:
                    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                    st.button("💾 Simpan status", key="_map_save_status", on_click=_map_set_status,
                              args=(_sel_key,), type="primary", width="stretch")
                with _mc3:
                    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                    st.button("🗑️ Hapus", key="_map_delete", on_click=_map_delete_row,
                              args=(_sel_key,), width="stretch",
                              help="Membuang merchant ini dari data (bisa dibatalkan lewat \"Batalkan semua edit tabel\").")
            else:
                st.caption("👆 Klik sebuah titik di peta untuk mengubah status atau menghapusnya.")
            if _outliers:
                st.caption("🔴 Cincin merah = tampak janggal (koordinat mungkin salah).")
        if _exclude_outliers:
            df = df.drop(index=list(_outliers)).reset_index(drop=True)
            if df.empty:
                st.info("Semua titik terdeteksi janggal — periksa koordinatnya di tabel Data Awal.")
                st.stop()

        # Merchant berstatus "sudah akuisisi" / "belum tertarik" tidak dimasukkan ke rute.
        _skip_status = df["status"].isin(STATUS_EXCLUDED)
        _n_excl_status = int(_skip_status.sum())
        _n_acq = int((df["status"] == STATUS_AKUISISI).sum())
        _n_not = int((df["status"] == STATUS_TIDAK).sum())
        _n_lost = int((df["status"] == STATUS_HILANG).sum())
        if _skip_status.any():
            df = df[~_skip_status].reset_index(drop=True)
            if df.empty:
                st.info("Semua merchant berstatus sudah akuisisi / belum tertarik / tidak ditemukan — tidak ada yang bisa dirutekan.")
                st.stop()
        st.session_state.row_key_map = {}
        for _k, _n, _la, _lo in zip(df["_row_key"], df["merchant_name"], df["latitude"], df["longitude"]):
            st.session_state.row_key_map.setdefault(_row_sig(_n, _la, _lo), _k)
        df = df.drop(columns=["_row_key"], errors="ignore")

        _n_priority = int(df["prioritas"].apply(is_truthy).sum()) if "prioritas" in df.columns else 0
        _has_hours = "jam_buka" in df.columns or "jam_tutup" in df.columns
        _n_hours_rows = 0
        if _has_hours:
            _n_hours_rows = int(sum(
                1 for _i in range(len(df))
                if _parse_hhmm(df["jam_buka"].iloc[_i] if "jam_buka" in df.columns else None) is not None
                or _parse_hhmm(df["jam_tutup"].iloc[_i] if "jam_tutup" in df.columns else None) is not None
            ))
        _chk_items = []
        if _n_nocoord:
            _chk_items.append(f"📍 **{_n_nocoord}** belum punya koordinat — belum ikut rute (lengkapi di atas)")
        if _outliers:
            _chk_items.append(f"⚠️ **{len(_outliers)}** titik tampak janggal — " + ("dikeluarkan dari rute" if _exclude_outliers else "tetap diikutkan"))
        if n_dup:
            _chk_items.append(f"🧹 **{n_dup}** baris duplikat — " + ("sudah dihapus" if remove_dups else "masih diikutkan"))
        if _n_excl_status:
            _chk_items.append(f"🚫 **{_n_excl_status}** tidak diikutkan karena status (sudah akuisisi {_n_acq}, belum tertarik {_n_not}, tidak ditemukan {_n_lost})")
        _info_items = []
        if _n_priority:
            _info_items.append(f"⭐ {_n_priority} merchant prioritas dikunjungi lebih dulu")
        if _n_hours_rows:
            _info_items.append(f"🕒 {_n_hours_rows} merchant punya jam operasional")
        with st.container(border=True):
            st.markdown(f"**✅ Pemeriksaan data — {len(df)} merchant siap dirutekan**")
            if _chk_items:
                st.markdown("\n".join("- " + _x for _x in _chk_items))
                st.caption("Perbaiki lewat **Lihat & Edit Data Awal** atau **Pratinjau peta** di atas, atau biarkan kalau memang disengaja.")
            else:
                st.caption("Tidak ada masalah — semua titik punya koordinat dan tampak wajar.")
            if _info_items:
                st.caption(" · ".join(_info_items))

        section_header(
            "2️⃣", "Atur Pembagian Rute",
            "Tentukan jumlah rute, titik awal, dan waktu kunjungan",
        )
        if IS_PRO:
            render_preset_panel()
        dp_on = False
        dp_balance = False
        dp_n, dp_cap, dp_lock, _dp_days_est = 1, 12, False, 0
        dp_names, dp_rows, dp_days_sel, dp_start_date, dp_end_date = [], [], [], None, None
        if IS_PRO:
            _ss = st.session_state
            _today = datetime.date.today()
            _ss.setdefault("dp_on", False)
            _ss.setdefault("dp_n", 2)
            _ss.setdefault("dp_days", [])   # hari kerja dipilih sendiri (tidak terisi otomatis)
            _ss.setdefault("dp_lock", False)
            for _k in ["dp_on", "dp_n", "dp_cap", "dp_days", "dp_lock", "dp_start_date", "dp_end_date"] + [
                f"{_p}_{_i}" for _i in range(30) for _p in ("dp_name", "dp_start")
            ]:
                if _k in _ss:
                    _ss[_k] = _ss[_k]   # jaga isian walau bagian ini sempat tidak tampil
            with st.container(border=True):
                dp_on = st.checkbox(
                    "👥 Pembagian petugas & hari kerja", key="dp_on",
                    help="Bagi merchant ke beberapa petugas (tiap petugas satu wilayah, dengan titik awal masing-masing) lalu ke hari "
                         "kerja. Tiap petugas-hari menjadi satu rute. Cocok untuk satu hari dengan banyak petugas maupun untuk "
                         "ratusan merchant lintas hari. Menggantikan pengaturan jumlah rute.",
                )
                if dp_on:
                    dc1, dc2 = st.columns(2)
                    with dc1:
                        dp_n = int(st.number_input("Jumlah petugas", min_value=1, max_value=30, step=1, key="dp_n"))
                    with dc2:
                        _cap_in = st.number_input("Maks. merchant per petugas per hari (opsional)", min_value=1, max_value=60,
                                                  step=1, value=None, key="dp_cap", placeholder="Kosong = tanpa batas",
                                                  help="Kosong = tiap petugas menyelesaikan semua merchant wilayahnya dalam satu hari "
                                                       "(tanpa batas harian). Isi untuk memecah ke beberapa hari kerja.")
                    dd1, dd2 = st.columns(2)
                    with dd1:
                        dp_start_date = st.date_input("Mulai tanggal (opsional)", value=None, key="dp_start_date",
                                                      help="Kosongkan bersama hari kerja kalau tidak perlu tanggal — hasil rute hanya "
                                                           "menampilkan petugas (dan urutan hari).")
                    with dd2:
                        dp_end_date = st.date_input("Sampai tanggal (opsional)", value=None, key="dp_end_date",
                                                    help="Batas akhir jadwal. Berguna untuk membatasi ke minggu tertentu: mis. hari kerja "
                                                         "Senin–Selasa, mulai Senin 2 Nov, sampai Selasa 3 Nov.")
                    dp_days_sel = st.multiselect(
                        "Hari kerja (opsional)", ID_DAYS, key="dp_days", placeholder="Kosong = tanpa hari/tanggal (atau semua hari berurutan kalau tanggal diisi)",
                        help="Pilih hanya kalau ada hari yang dilewati (mis. Senin–Jumat saja). Dibiarkan kosong, hari kerja dihitung "
                             "berurutan setiap hari mulai tanggal mulai (akhir pekan ikut). Untuk satu hari dengan beberapa petugas, "
                             "biarkan kosong atau pilih satu hari.",
                    )
                    dp_lock = st.checkbox(
                        "🔒 Kunci wilayah petugas", key="dp_lock",
                        help="Merchant yang sudah punya kolom `petugas` (nama sama dengan daftar di bawah) tetap di petugas "
                             "itu; merchant baru masuk ke wilayah petugas terdekat. Simpan wilayah dari hasil rute lewat "
                             "tombol 🔒 di tab Ringkasan, atau isi kolom petugas di Lihat & Edit Data Awal / Excel.",
                    )
                    dp_balance = st.checkbox(
                        "⏱️ Seimbangkan beban waktu antar rute",
                        value=st.session_state.balance_time_flag,
                        key=_wk("_balance_time_widget"),
                        on_change=_sync_balance_time,
                        help=(
                            "Tanpa ini, satu hari kerja bisa 2 jam sementara hari lain 5 jam. Dengan ini, merchant di "
                            "perbatasan antar hari milik petugas yang sama dipindahkan supaya durasi (perjalanan + "
                            "kunjungan) tiap hari lebih mirip. Wilayah dan titik awal petugas tidak berubah, dan batas "
                            "merchant per hari tetap dihormati. Perkiraan memakai jarak garis lurus; rute akhir tetap "
                            "dihitung dengan jarak jalan asli."
                        ),
                    )
                    st.markdown("**Petugas** — nama dan titik awal (rumah/kantor, opsional)")
                    for _i in range(dp_n):
                        pc1, pc2 = st.columns([1, 2])
                        with pc1:
                            _nm = st.text_input(f"Nama petugas {_i + 1}", key=f"dp_name_{_i}", placeholder=f"Petugas {_i + 1}",
                                                label_visibility="collapsed")
                        with pc2:
                            _loc = st.text_input(f"Titik awal petugas {_i + 1}", key=f"dp_start_{_i}",
                                                 placeholder="Titik awal: link Google Maps atau koordinat (opsional)",
                                                 label_visibility="collapsed")
                        dp_names.append(_nm.strip() or f"Petugas {_i + 1}")
                        dp_rows.append((_nm.strip(), _loc))
                    if len(set(n.lower() for n in dp_names)) < len(dp_names):
                        st.warning("⚠️ Ada nama petugas yang kembar — beri nama berbeda supaya wilayahnya tidak tertukar.")
                    _n_eff = min(int(st.session_state.nearest_n_flag), len(df)) if (IS_PRO and st.session_state.nearest_on_flag and len(df) >= 3) else len(df)
                    _per = math.ceil(_n_eff / dp_n)
                    dp_cap = int(_cap_in) if _cap_in else max(1, _per)   # kosong = tanpa batas harian
                    _dp_days_est = math.ceil(_per / dp_cap)
                    _weeks = math.ceil(_dp_days_est / (len(dp_days_sel) or 7))
                    _dated = bool(dp_days_sel or dp_start_date or dp_end_date)
                    st.caption(
                        f"📅 Perkiraan: {_n_eff} merchant → {dp_n} petugas × ±{_dp_days_est} hari kerja"
                        + (f" (≈{_weeks} minggu)" if _dated else "") + f", ±{dp_n * _dp_days_est} rute."
                    )
                    if dp_end_date:
                        _wd0 = {ID_DAYS.index(x) for x in dp_days_sel} or set(range(7))
                        _st0 = dp_start_date or _today
                        _avail = len([d for d in make_work_dates(_st0, _wd0, 400) if d <= dp_end_date])
                        if dp_end_date < _st0:
                            st.warning("⚠️ Tanggal akhir lebih awal dari tanggal mulai.")
                        elif _avail < _dp_days_est:
                            _need_cap = math.ceil(_per / max(_avail, 1))
                            _fit_n = dp_n * max(_avail, 1) * dp_cap
                            st.warning(
                                f"⚠️ Hanya tersedia {_avail} hari kerja dalam rentang ini, sedangkan butuh ±{_dp_days_est}. "
                                f"Naikkan 'Maks. merchant per petugas per hari' jadi ≥{_need_cap}, tambah petugas, atau aktifkan "
                                f"'Ambil hanya merchant terdekat' (≈{_fit_n} merchant muat)."
                            )
                        else:
                            st.caption(f"✅ {_avail} hari kerja tersedia dalam rentang ini (butuh ±{_dp_days_est}).")
        use_multi_depot = False   # multi-depot sudah dihapus dari tampilan (digantikan Pembagian petugas & hari kerja)
        with st.container(border=True):
            st.markdown("**🧭 Pembagian rute**")
            if dp_on:
                plan_mode = PLAN_MAX
                max_points_per_route, target_routes = dp_cap, None
                n_cluster_default = max(1, dp_n * _dp_days_est)
                split_mode, balance_time = SPLIT_AUTO, dp_balance   # dp_balance ikut tanda tangan pengaturan hasil
                st.info(
                    "Dinonaktifkan karena **Pembagian petugas & hari kerja** aktif — jumlah rute ditentukan oleh jumlah petugas, "
                    "hari kerja, dan batas merchant per hari di atas.",
                    icon="🔒",
                )
                st.radio("Cara menentukan jumlah rute", [PLAN_MAX, PLAN_COUNT], index=0, key="_plan_off",
                         horizontal=not IS_MOBILE, disabled=True)
                st.number_input("Maksimal merchant per rute", min_value=1, max_value=max(60, int(dp_cap)), value=int(dp_cap), step=1,
                                key="_cap_off", disabled=True)
            else:
                if use_multi_depot:
                    st.info(
                        "Multi-depot aktif — atur jumlah rute di bawah, lalu tentukan titik awal tiap rute di bagian "
                        "**Titik awal**.",
                        icon="🏭",
                    )
                plan_mode = st.radio(
                    "Cara menentukan jumlah rute",
                    [PLAN_MAX, PLAN_COUNT],
                    index=0 if st.session_state.plan_mode_flag == PLAN_MAX else 1,
                    key=_wk("_plan_widget"),
                    on_change=_sync_plan,
                    horizontal=not IS_MOBILE,
                )
                max_points_per_route, target_routes = _plan_control(df, plan_mode)
                n_cluster_default = target_routes or math.ceil(len(df) / max_points_per_route)
                st.caption(f"🧭 Perkiraan: **{len(df)} merchant → {n_cluster_default} rute**")

                if target_routes is not None:
                    split_mode = SPLIT_AUTO
                    st.caption(
                        f"Merchant dibagi ke {target_routes} rute mengikuti area lokasi, "
                        f"maksimal {max_points_per_route} merchant per rute supaya beban merata."
                    )
                elif n_cluster_default > 1 and IS_PRO and not use_multi_depot:
                    split_mode = st.radio(
                        "Cara membagi rute",
                        [SPLIT_AUTO, SPLIT_FULL],
                        index=0 if st.session_state.split_mode_flag == SPLIT_AUTO else 1,
                        key=_wk("_split_widget"),
                        on_change=_sync_split,
                        horizontal=not IS_MOBILE,
                        help=(
                            "Otomatis: merchant dikelompokkan menurut area/kedekatan lokasi, jadi jarak tempuh "
                            "lebih pendek, tapi isi tiap rute bisa berbeda (selalu di bawah atau sama dengan maksimal). "
                            "Isi penuh: tiap rute diisi sampai batas maksimal dan sisanya masuk rute terakhir, "
                            "tapi rute bisa lebih melebar karena merchant dari area lain ikut terambil."
                        ),
                    )
                    _n, _k, _m = len(df), n_cluster_default, max_points_per_route
                    if split_mode == SPLIT_FULL:
                        full_sizes = [_m] * (_k - 1) + [_n - _m * (_k - 1)]
                        st.caption(f"Isi tiap rute: {_fmt_sizes(full_sizes)} merchant.")
                    else:
                        st.caption(
                            f"Pembagian mengikuti area lokasi — {_k} rute, masing-masing maksimal {_m} merchant. "
                            "Pilih **Isi penuh** kalau ingin tiap rute berisi tepat sebanyak maksimal."
                        )
                elif n_cluster_default > 1:
                    split_mode = SPLIT_AUTO   # Mode Basic: selalu otomatis per area ("Isi penuh" ada di Mode Pro)
                    st.caption(
                        f"Merchant dikelompokkan menurut area lokasi — {n_cluster_default} rute, masing-masing maksimal "
                        f"{max_points_per_route} merchant."
                    )
                else:
                    split_mode = st.session_state.split_mode_flag if IS_PRO else SPLIT_AUTO

                # Pemerataan beban waktu: hanya relevan kalau ada >1 rute hasil pengelompokan per area.
                if IS_PRO and n_cluster_default > 1 and not use_multi_depot and split_mode == SPLIT_AUTO:
                    balance_time = st.checkbox(
                        "⏱️ Seimbangkan beban waktu antar rute",
                        value=st.session_state.balance_time_flag,
                        key=_wk("_balance_time_widget"),
                        on_change=_sync_balance_time,
                        help=(
                            "Tanpa ini, rute dibagi berdasarkan area dan jumlah merchant, jadi satu rute bisa 2 jam "
                            "sementara yang lain 5 jam. Dengan ini, merchant di perbatasan antar rute dipindahkan supaya "
                            "durasi (perjalanan + kunjungan) tiap rute lebih mirip. Perkiraan memakai jarak garis lurus; "
                            "rute akhir tetap dihitung dengan jarak jalan asli."
                            + (" Batas maksimal merchant per rute tetap dihormati." if target_routes is None
                               else " Di mode jumlah rute, jumlah merchant per rute boleh berbeda demi menyamakan waktu.")
                        ),
                    )
                else:
                    balance_time = False


        with st.container(border=True):
            st.markdown("**📍 Titik awal**")
            if dp_on:
                starting_link = ""
            else:
                starting_link = st.text_input(
                    "📍 Titik Awal (opsional)",
                    value=st.session_state.starting_link_saved,
                    key=_wk("_starting_link_widget"),
                    on_change=_sync_starting_link,
                    placeholder="Link Google Maps atau koordinat (-7.5665, 110.8167)",
                    help=(
                        "Misalnya lokasi gudang atau toko pusat. Kalau diisi, titik ini otomatis jadi awal setiap rute dan urutan "
                        "kunjungan dihitung dari titik ini. Cara dapat link: buka lokasinya di Google Maps → Bagikan → Salin link. "
                        "Atau tempel koordinatnya langsung. Kosong = titik mulai dipilih otomatis."
                    ),
                )
            use_my_loc = st.checkbox(
                "🧭 Di lapangan, mulai navigasi Google Maps dari lokasi petugas",
                value=st.session_state.start_mode_saved == "mylocation",
                key=_wk("_start_mode_widget"),
                on_change=_sync_start_mode,
                help="Rute tetap dihitung dari titik awal (di Pembagian petugas & hari kerja: titik awal tiap petugas), tetapi saat link "
                     "Google Maps dibuka, navigasi dimulai dari posisi GPS petugas pada saat itu (bukan titik awal). Cocok bila "
                     "petugas berangkat dari rumah atau lokasi lain.",
            )
            if use_my_loc:
                st.caption(
                    "📍 Urutan rute dihitung dari titik awal" + (" tiap petugas" if dp_on else " di atas") + ". Saat link Google Maps "
                    "dibuka, navigasi dimulai dari **lokasi petugas saat itu**; aktifkan GPS dan izinkan Google Maps memakai lokasi."
                    + ("" if (starting_link or dp_on) else " Titik awal di atas kosong, jadi titik mulai rute dipilih otomatis; isi titik awal supaya urutan sesuai tempat berangkat sebenarnya.")
                )

            nearest_on = IS_PRO and st.checkbox(
                "🎯 Ambil hanya merchant terdekat dari titik awal",
                value=bool(st.session_state.nearest_on_flag),
                key=_wk("_nearest_on_widget"),
                on_change=_sync_nearest_on,
                disabled=len(df) < 3,
                help="Dari semua data, hanya N merchant yang paling dekat dengan titik awal yang dibuatkan rute (jarak garis lurus). "
                     "Di Pembagian petugas & hari kerja: dekat dengan titik awal petugas mana pun. "
                     "Sisanya tidak ikut kali ini; setelah merchant dikunjungi dan statusnya diperbarui, buat rute lagi untuk gelombang berikutnya.",
            ) and len(df) >= 3
            nearest_n = len(df)
            if nearest_on:
                nearest_n = int(st.number_input(
                    f"Jumlah merchant yang diambil (dari {len(df)})", min_value=2, max_value=max(2, len(df)),
                    value=int(min(max(2, st.session_state.nearest_n_flag), max(2, len(df)))), step=1,
                    key=_wk("_nearest_n_widget"), on_change=_sync_nearest_n,
                ))
                _have_start = bool(starting_link) or (dp_on and any(str(_l).strip() for _, _l in dp_rows))
                if not _have_start:
                    st.warning(("Isi titik awal minimal satu petugas di Pembagian petugas & hari kerja" if dp_on else "Isi **Titik Awal** di atas")
                               + " dulu: tanpa titik awal, merchant terdekat tidak bisa ditentukan dan semua merchant tetap dibuatkan rute.", icon="📍")
                else:
                    st.caption(f"🎯 {min(nearest_n, len(df))} merchant terdekat dari titik awal" + (" petugas" if dp_on else "") + " (garis lurus) akan dibuatkan rute; "
                               "pembagian ke beberapa rute tetap mengikuti pengaturan di atas.")

            use_multi_depot = False
            depot_rows_raw = []
            if dp_on:
                starting_link = ""  # tidak dipakai di Pembagian petugas & hari kerja
                st.info(
                    "Titik awal tiap petugas diisi di bagian **Pembagian petugas & hari kerja** di atas (kosong = titik mulai dipilih "
                    "otomatis). Kotak navigasi di atas tetap berlaku untuk rute semua petugas.",
                    icon="📍",
                )

        if not IS_PRO:
            # Mode Basic: jumlah rute tetap bisa diatur (di atas), tapi jam
            # mulai/durasi kunjungan/arah rute pakai nilai terakhir yang
            # tersimpan (default: mulai 08:00, tanpa durasi kunjungan, satu
            # arah). Ganti ke Mode Pro di sidebar untuk mengatur ini juga.
            start_time = st.session_state.start_time_flag
            visit_minutes = st.session_state.visit_minutes_flag
            round_trip = st.session_state.round_trip_flag
            st.caption(
                "💡 Mode Basic: rute dimulai 08:00, tanpa durasi kunjungan, satu arah, dibagi otomatis per area. "
                "Butuh jam mulai & durasi kunjungan, pulang-pergi, prioritas, jam operasional, pembagian petugas & hari kerja, seimbangkan "
                "beban waktu, atau simpan sesi? Pindah ke **🛠️ Pro** di sidebar."
            )
        else:
            with st.container(border=True):
                st.markdown("**⏰ Waktu & arah**")
                t1, t2 = st.columns(2)
                with t1:
                    start_time = st.time_input(
                        "⏰ Jam mulai",
                        value=st.session_state.start_time_flag,
                        key=_wk("_start_time_widget"),
                        on_change=_sync_start_time,
                        step=300,
                        help="Dipakai untuk menghitung perkiraan jam tiba di tiap merchant.",
                    )
                with t2:
                    visit_minutes = st.number_input(
                        "🏪 Durasi kunjungan per toko (menit)",
                        min_value=0, max_value=480, value=int(st.session_state.visit_minutes_flag), step=1,
                        key=_wk("_visit_widget"),
                        on_change=_sync_visit,
                        help="Waktu yang dihabiskan di tiap merchant. 0 = hanya hitung waktu perjalanan.",
                    )

                round_trip = st.checkbox(
                    "🔁 Kembali ke titik awal setelah rute selesai",
                    value=st.session_state.round_trip_flag,
                    key=_wk("_round_trip_widget"),
                    on_change=_sync_round_trip,
                    help=(
                        "Aktif: rute melingkar dan jarak/waktu sudah termasuk perjalanan pulang. "
                        "Nonaktif: rute satu arah, berhenti di merchant terakhir. "
                        "Kalau Titik Awal kosong, rute dimulai dari titik yang paling efisien."
                    ),
                )


        hours_opt = bool(IS_PRO and _hours_opt_choice and _n_hours)   # ceklisnya ada di Lihat & Edit Data Awal


        _plan_txt = (
            f"{dp_n} petugas × ±{_dp_days_est} hari kerja (maks. {dp_cap}/hari)" if dp_on else
            f"{target_routes} rute (maks. {max_points_per_route}/rute)" if target_routes is not None
            else f"{n_cluster_default} rute (maks. {max_points_per_route} merchant/rute"
                 + (", isi penuh" if n_cluster_default > 1 and split_mode == SPLIT_FULL else
                    ", otomatis per area" if n_cluster_default > 1 else "") + ")"
        )
        st.info(
            f"**Ringkasan:** {len(df)} merchant → {_plan_txt} · mulai {start_time:%H:%M} · "
            + (f"{int(visit_minutes)} menit/toko" if visit_minutes else "tanpa durasi kunjungan")
            + " · " + ("pulang-pergi" if round_trip else "satu arah")
            + (f" · {min(nearest_n, len(df))} merchant terdekat" if nearest_on else "")
            + " · titik awal: " + ("per petugas" if dp_on else ("sesuai isian" if starting_link else "otomatis (paling efisien)")) + (" · navigasi dari lokasi petugas" if use_my_loc else "")
            + (" · urut sesuai jam buka/tutup" if hours_opt else ""),
            icon="🧾",
        )

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        run = st.button("🚀 Buat Rute Optimal Sekarang", type="primary", width='stretch')

        # Fingerprint of the current input+settings, so stale results (from a
        # previous file/slider value) don't linger after the inputs change.
        data_fingerprint = (
            len(df), tuple(df["merchant_name"]), max_points_per_route, target_routes, starting_link,
            round_trip, split_mode, int(visit_minutes), start_time.strftime("%H:%M"),
            use_multi_depot, tuple(depot_rows_raw), balance_time, hours_opt, use_my_loc,
            (nearest_n if nearest_on else None),
            (dp_n, tuple(dp_names), tuple(dp_rows), tuple(dp_days_sel), dp_cap, str(dp_start_date), str(dp_end_date), dp_lock) if dp_on else None,
        )

        if run:
            if len(df) < 2:
                st.warning("⚠️ Minimal butuh 2 titik untuk bisa membuat rute.")
                st.stop()

            # Daftar titik awal per rute (kalau multi-depot aktif) — resolve DULU.
            # Baris k = titik awal Rute k; baris kosong = rute itu dimulai otomatis.
            depots = []
            if use_multi_depot:
                depots, depot_errs = parse_depot_rows(depot_rows_raw)
                for derr in depot_errs:
                    st.warning(f"⚠️ {derr}")
                if not depots:
                    st.error("❌ Multi-depot aktif tapi belum ada titik awal yang valid. Isi titik awal minimal satu rute, atau matikan multi-depot.")
                    st.stop()

            with fancy_loading("Membuat rute optimal", "Mengelompokkan titik dan mencari rute tercepat di jalan asli", pct=0.03) as _ld:
                # Titik awal tunggal (dipakai kalau multi-depot tidak aktif). Di-resolve SEBELUM
                # pengelompokan karena pemerataan beban waktu ikut memperhitungkan titik awal.
                start_name, start_lat, start_lon = "START POINT", None, None
                if not depots and starting_link:
                    coord_lat = coord_lon = None
                    if "http" not in starting_link.lower():
                        coord_lat, coord_lon, _coord_err = parse_coordinate_text(starting_link)
                    if coord_lat is not None:
                        start_name, start_lat, start_lon = "Titik Awal", coord_lat, coord_lon
                    else:
                        parsed_name, start_lat, start_lon = extract_google_maps_data(starting_link)
                        start_name = parsed_name or "START POINT"

                nearest_info = None
                if nearest_on and not dp_on and not depots and start_lat and start_lon:
                    df, nearest_info = pick_nearest(df, start_lat, start_lon, nearest_n)
                balance_info = None
                dp_meta = {}
                route_depot = {}
                if dp_on:
                    _starts = [None] * dp_n
                    _dp_deps, _dp_errs = parse_depot_rows(dp_rows)
                    for _e in _dp_errs:
                        st.warning("⚠️ " + _e.replace("Titik awal Rute", "Titik awal petugas").replace("rute ini dimulai otomatis", "dimulai otomatis"))
                    for _d in _dp_deps:
                        _starts[_d["row"]] = (_d["lat"], _d["lon"])
                    if nearest_on:
                        _pts = [_x for _x in _starts if _x]
                        if _pts and nearest_n < len(df):
                            _dd = np.array([min(haversine(_a, _b, _la, _lo) for _a, _b in _pts)
                                            for _la, _lo in zip(df["latitude"], df["longitude"])])
                            _keep = np.sort(np.argsort(_dd, kind="stable")[:nearest_n])
                            nearest_info = {"picked": int(nearest_n), "total": int(len(df)), "max_km": float(_dd[_keep].max())}
                            df = df.iloc[_keep].reset_index(drop=True)
                    _assigned = None
                    if dp_lock and "petugas" in df.columns:
                        _by_name = {n.strip().lower(): i for i, n in enumerate(dp_names)}
                        _assigned = np.array([_by_name.get(str(v).strip().lower(), -1) for v in df["petugas"]], dtype=int)
                    _labels, _meta = plan_multi_day(
                        df["latitude"], df["longitude"], dp_n, dp_cap, starts=_starts, assigned=_assigned,
                    )
                    df["route"] = _labels
                    if balance_time:
                        # Per petugas: pindahkan titik di perbatasan antar hari kerja miliknya. Lintas petugas tidak
                        # disentuh supaya wilayah (dan kunci wilayah) serta titik awal tiap petugas tetap utuh.
                        _bal_parts = []
                        for _p in sorted({_m["p"] for _m in _meta}):
                            _rids = [_m["route_id"] for _m in _meta if _m["p"] == _p]
                            if len(_rids) < 2:
                                continue
                            _mask = df["route"].isin(_rids).to_numpy()
                            _sub = df[_mask]
                            _nl, _inf = balance_by_time(
                                _sub, _sub["route"].to_numpy(), int(visit_minutes), start=_starts[_p], max_points=dp_cap,
                            )
                            df.loc[_mask, "route"] = _nl
                            _bal_parts.append(_inf)
                        if _bal_parts:
                            # selisih = rata-rata per petugas (nilai terburuk saja menyembunyikan perbaikan di petugas lain);
                            # hari terlama = yang terlama di antara semua petugas
                            balance_info = {
                                "before_spread_min": float(np.mean([_i["before_spread_min"] for _i in _bal_parts])),
                                "after_spread_min": float(np.mean([_i["after_spread_min"] for _i in _bal_parts])),
                                "before_max_min": max(_i["before_max_min"] for _i in _bal_parts),
                                "after_max_min": max(_i["after_max_min"] for _i in _bal_parts),
                                "scope": "petugas",
                            }
                    _dateless = not (dp_days_sel or dp_start_date or dp_end_date)   # tanpa tanggal & hari
                    _need_days = max(m["day"] for m in _meta) + 1
                    if not _dateless:
                        _wd = {ID_DAYS.index(x) for x in dp_days_sel} or set(range(7))   # kosong = semua hari berurutan
                        _st_d = dp_start_date or datetime.date.today()
                        _dates = make_work_dates(_st_d, _wd, _need_days)
                        if dp_end_date:
                            _ok = [d for d in make_work_dates(_st_d, _wd, 400) if d <= dp_end_date]
                            if len(_ok) < _need_days:
                                st.error(
                                    f"❌ Jadwal butuh {_need_days} hari kerja, tetapi hanya {len(_ok)} hari tersedia sampai "
                                    f"{dp_end_date.strftime('%d/%m/%Y')}. Naikkan maks. merchant per hari, tambah petugas, "
                                    f"pakai 'Ambil hanya merchant terdekat', atau perpanjang tanggal akhir."
                                )
                                st.stop()
                    for _m in _meta:
                        if _dateless:
                            dp_meta[_m["route_id"]] = {"petugas": dp_names[_m["p"]], "date": "", "hari": "", "hari_ke": _m["day"] + 1}
                            continue
                        _dt = _dates[_m["day"]]
                        dp_meta[_m["route_id"]] = {
                            "petugas": dp_names[_m["p"]], "date": _dt.isoformat(), "hari": fmt_day_label(_dt, short=False),
                            "hari_ke": _m["day"] + 1,
                        }
                        _sp = _starts[_m["p"]]
                        route_depot[_m["route_id"]] = (
                            {"name": f"Titik awal {dp_names[_m['p']]}", "lat": _sp[0], "lon": _sp[1], "row": _m["p"]}
                            if _sp else None
                        )
                else:
                    # Jumlah rute: sesuai pengaturan Langkah 2. Dengan multi-depot, tiap rute lalu dipasangkan
                    # dengan titik awal yang diisi untuk rute itu (lihat assign_routes_to_depots).
                    n_cluster = target_routes or math.ceil(len(df) / max_points_per_route)
                    n_cluster = max(1, min(n_cluster, len(df)))
                    if target_routes is None and n_cluster > 1 and split_mode == SPLIT_FULL and not depots:
                        df["route"] = fill_clusters(df, max_points_per_route)
                    else:
                        coords = df[["latitude", "longitude"]]
                        kmeans = KMeans(n_clusters=n_cluster, random_state=42, n_init=10)
                        df["route"] = kmeans.fit_predict(coords)
                        df = balance_clusters(df, max_points_per_route)
                        if balance_time and df["route"].nunique() > 1:
                            _start_xy = (start_lat, start_lon) if (start_lat and start_lon) else None
                            # Mode "jumlah rute": batas maksimal per rute hanya turunan (pembulatan),
                            # jadi tidak dipakai. Mode "maksimal titik per rute": batasnya tetap dihormati.
                            _cap = max_points_per_route if target_routes is None else None
                            new_labels, balance_info = balance_by_time(
                                df, df["route"].to_numpy(), int(visit_minutes), start=_start_xy, max_points=_cap,
                            )
                            df["route"] = new_labels
                    route_depot = {}
                    if depots:
                        _new_of, route_depot = assign_routes_to_depots(df, depots)
                        df["route"] = df["route"].map(_new_of)

                all_routes = []
                route_summaries = []
                hours_opt_routes = 0
                hours_opt_failed = 0
                any_fallback_used = False
                osrm_errors = []
                base_date = datetime.date.today()
                start_dt = datetime.datetime.combine(base_date, start_time)
                visit_sec = int(visit_minutes) * 60
                _route_ids = sorted(df["route"].unique())
                _ld.update(sub=f"Menghitung {len(_route_ids)} rute di jalan asli", pct=0.1)
                for _ri, route_id in enumerate(_route_ids, start=1):
                    _ld.update(sub=f"Menghitung rute {_ri} dari {len(_route_ids)}", pct=0.1 + 0.88 * (_ri - 1) / len(_route_ids))
                    route_df = df[df["route"] == route_id].reset_index(drop=True)

                    if depots or dp_on:
                        chosen_depot = route_depot.get(route_id)
                        if chosen_depot:
                            route_start_name = chosen_depot["name"]
                            route_start_lat, route_start_lon = chosen_depot["lat"], chosen_depot["lon"]
                        elif dp_on:  # petugas tanpa titik awal sendiri → pakai titik awal tunggal (kalau ada)
                            route_start_name, route_start_lat, route_start_lon = start_name, start_lat, start_lon
                        else:  # baris titik awal rute ini dikosongkan → titik mulai dipilih otomatis
                            route_start_name, route_start_lat, route_start_lon = "START POINT", None, None
                    else:
                        route_start_name, route_start_lat, route_start_lon = start_name, start_lat, start_lon

                    if route_start_lat and route_start_lon:
                        start_df = pd.DataFrame(
                            [{"merchant_name": route_start_name, "latitude": route_start_lat, "longitude": route_start_lon}]
                        )
                        route_df = pd.concat([start_df, route_df], ignore_index=True)

                    distance_matrix, duration_matrix, used_real_roads, osrm_error = get_route_matrices(route_df)
                    any_fallback_used = any_fallback_used or not used_real_roads
                    if osrm_error:
                        osrm_errors.append(osrm_error)

                    has_start = bool(route_start_lat and route_start_lon)

                    # Merchant prioritas (kolom opsional "prioritas"): dikunjungi lebih
                    # dulu, baru lanjut ke sisanya.
                    if "prioritas" in route_df.columns:
                        p_mask = route_df["prioritas"].apply(is_truthy)
                        priority_idx = [i for i in range(len(route_df)) if p_mask.iloc[i] and not (has_start and i == 0)]
                    else:
                        priority_idx = []

                    tw = build_time_windows(route_df, start_dt, base_date, has_start) if hours_opt else {}
                    tw_order = None
                    if tw:
                        tw_order = solve_tsp_time_windows(
                            distance_matrix, duration_matrix, tw, visit_sec,
                            round_trip=round_trip, first_is_start=has_start,
                        )
                    if tw and tw_order is None:
                        hours_opt_failed += 1
                    if tw_order is not None:
                        best_route = tw_order
                        hours_opt_routes += 1
                    elif priority_idx:
                        other_idx = [
                            i for i in range(len(route_df))
                            if not (has_start and i == 0) and i not in priority_idx
                        ]
                        best_route = solve_tsp_with_priority(
                            distance_matrix, priority_idx, other_idx, has_start, round_trip
                        )
                    else:
                        best_route = solve_tsp(distance_matrix, round_trip=round_trip, fixed_start=has_start)

                    # waktu tunggu hanya dipakai kalau urutan berasal dari optimasi jam operasional
                    open_secs = {i: lo for i, (lo, _hi) in tw.items() if lo and lo > 0} if tw_order is not None else {}
                    fin = finalize_route(
                        route_df, best_route, distance_matrix, duration_matrix, route_id,
                        start_dt, visit_sec, has_start, round_trip, base_date, open_secs,
                    )
                    all_routes.append(fin["df"])

                    # Pembanding "sebelum optimasi": mengunjungi titik sesuai urutan di file
                    # (titik awal tetap di depan), pakai matriks jarak/waktu yang sama.
                    naive_order = list(range(len(route_df)))
                    naive_distance_km = route_leg_sum(distance_matrix, naive_order, round_trip) / 1000
                    naive_duration_sec = route_leg_sum(duration_matrix, naive_order, round_trip)

                    if dp_on:  # nama petugas rute ini = petugas pemegang wilayahnya (bisa diubah lagi di tiap rute)
                        st.session_state.driver_names[route_id] = dp_meta[route_id]["petugas"]
                        st.session_state[f"driver_{route_id}"] = dp_meta[route_id]["petugas"]
                    route_summaries.append(
                        {
                            "route_id": route_id,
                            **fin,
                            "naive_distance_km": naive_distance_km,
                            "naive_duration_sec": naive_duration_sec,
                            "real_roads": used_real_roads,
                            "round_trip": round_trip,
                            "has_start": has_start,
                            "from_my_location": bool(use_my_loc),
                            "depot_name": route_start_name if has_start else "",
                            "depot_idx": (route_depot.get(route_id) or {}).get("row"),
                            "driver": st.session_state.driver_names.get(route_id, ""),
                            "petugas": dp_meta.get(route_id, {}).get("petugas", ""),
                            "tanggal": dp_meta.get(route_id, {}).get("date", ""),
                            "hari": dp_meta.get(route_id, {}).get("hari", ""),
                            "hari_ke": dp_meta.get(route_id, {}).get("hari_ke"),
                            # data mentah untuk ubah-urutan manual (tanpa memanggil OSRM lagi)
                            "route_df": route_df,
                            "distance_matrix": distance_matrix,
                            "duration_matrix": duration_matrix,
                            "order": list(best_route),
                            "optimal_order": list(best_route),
                            "optimal_distance_km": fin["distance_km"],
                            "optimal_duration_sec": fin["duration_sec"],
                            "manual": False,
                            "start_dt": start_dt,
                            "visit_sec_each": visit_sec,
                            "open_secs": open_secs,
                            "base_date": base_date,
                        }
                    )

            excel_bytes = build_excel_bytes(route_summaries)
            n_start_points = sum(1 for r in route_summaries if r["has_start"])

            # Persist everything needed to render the result, so later reruns
            # (e.g. clicking the map or the download button) don't wipe it out.
            st.session_state.route_result = {
                "fingerprint": data_fingerprint,
                "route_summaries": route_summaries,
                "total_points": len(df) + n_start_points,
                "excel_bytes": excel_bytes,
                "base_date": base_date.isoformat(),
                "start_label": start_time.strftime("%H:%M"),
                "start_ok": bool(start_lat and start_lon) or bool(depots),
                "start_link_given": bool(starting_link) and not bool(depots),
                "used_real_roads": not any_fallback_used,
                "osrm_error": osrm_errors[-1] if osrm_errors else None,
                "multi_depot_used": bool(depots),
                "multi_depot_overrode_single": bool(depots) and bool(starting_link),
                "n_depots": len(depots),
                "balance_info": balance_info,
                "nearest_info": nearest_info,
                "hours_opt_routes": hours_opt_routes,
                "hours_opt_failed": hours_opt_failed,
                "day_plan": dp_on,
            }

        result = st.session_state.get("route_result")
        if result and result["fingerprint"] == data_fingerprint:
            if result["start_link_given"] and not result["start_ok"]:
                st.warning("⚠️ Titik awal tidak dikenali (bukan link Google Maps atau koordinat yang valid), jadi dilewati — rute tetap dibuat tanpa titik awal khusus.")
            if result.get("multi_depot_overrode_single"):
                st.caption("ℹ️ Multi-depot aktif — daftar titik awal menggantikan field 'Titik Awal' tunggal untuk pembuatan rute ini.")

            if result.get("hours_opt_failed"):
                st.warning(
                    f"⚠️ Optimasi jam operasional gagal untuk {result['hours_opt_failed']} rute — rute itu memakai "
                    "urutan jarak terpendek biasa. Coba buat rute lagi."
                )
            if result.get("hours_opt_routes"):
                _n_out = sum(r.get("n_outside_hours", 0) for r in result["route_summaries"])
                if _n_out:
                    st.warning(
                        f"🕒 Urutan sudah dioptimalkan dengan jam operasional, tapi {_n_out} merchant tetap "
                        "diperkirakan tiba setelah jam tutup. Coba ubah **jam mulai** (Mode Pro), cek jam yang "
                        "salah di tabel Data Awal, atau pindahkan merchant itu ke hari lain."
                    )
                else:
                    st.success("🕒 Urutan dioptimalkan dengan jam operasional — semua merchant yang punya jam "
                               "diperkirakan dikunjungi saat buka (kalau perlu, petugas menunggu sampai buka).")

            if not result.get("used_real_roads", True):
                reason = result.get("osrm_error")
                st.warning(
                    "⚠️ Layanan rute jalan asli (OSRM) tidak bisa dipakai untuk sebagian/seluruh rute — "
                    "rute bertanda ⚠️ memakai estimasi garis lurus (±30 km/jam), jadi jarak & waktunya bisa "
                    "kurang akurat."
                    + (f" Penyebab terakhir: {reason}." if reason else "")
                    + " Coba tekan **Buat Rute Optimal** lagi, atau arahkan ke server OSRM sendiri lewat "
                    "pengaturan `OSRM_BASE_URL` di Secrets."
                )

            render_stepper(stepper_slot, 3)
            route_summaries = result["route_summaries"]
            # Nama petugas diselaraskan SEBELUM tombol unduh/WhatsApp dibuat (tombol kini ada di atas daftar rute,
            # jadi nama yang baru diketik di tiap rute harus sudah terbaca di sini).
            for _r0 in route_summaries:
                _rid0 = _r0["route_id"]
                _nm0 = st.session_state.get(f"driver_{_rid0}", st.session_state.driver_names.get(_rid0, ""))
                st.session_state.driver_names[_rid0] = _nm0
                _r0["driver"] = _nm0
            st.success(f"🎉 Rute berhasil dibuat! {len(route_summaries)} rute siap dipakai.")
            _near = result.get("nearest_info")
            if _near:
                st.caption(
                    f"🎯 Diambil **{_near['picked']} dari {_near['total']}** merchant terdekat dari titik awal "
                    f"(terjauh ±{_near['max_km']:.1f} km, garis lurus). {_near['total'] - _near['picked']} lainnya tidak masuk rute ini."
                )
            _bal = result.get("balance_info")
            if _bal and _bal["before_spread_min"] - _bal["after_spread_min"] > 1:
                _bal_lead = (
                    "⏱️ Beban waktu diseimbangkan antar hari kerja tiap petugas: selisih hari terlama–tercepat "
                    "(perkiraan, rata-rata per petugas) turun dari "
                    if _bal.get("scope") == "petugas" else
                    "⏱️ Beban waktu diseimbangkan: selisih rute terlama–tercepat (perkiraan) turun dari "
                )
                st.caption(
                    _bal_lead
                    + f"{format_duration(_bal['before_spread_min'] * 60)} menjadi {format_duration(_bal['after_spread_min'] * 60)}; "
                    f"yang terlama dari ±{format_duration(_bal['before_max_min'] * 60)} menjadi ±{format_duration(_bal['after_max_min'] * 60)}."
                )
            if result.get("multi_depot_used"):
                _used_dep = len({r.get("depot_idx") for r in route_summaries if r.get("depot_idx") is not None})
                if _used_dep < result.get("n_depots", 0):
                    st.caption(
                        f"ℹ️ {result['n_depots']} titik awal diisi, tapi rute yang terbentuk hanya {len(route_summaries)} "
                        f"sehingga {_used_dep} titik awal terpakai. Kurangi jumlah merchant per rute atau tambah jumlah rute."
                    )

            total_distance = sum(r["distance_km"] for r in route_summaries)
            total_duration = sum(r["duration_sec"] for r in route_summaries)
            total_visit = sum(r.get("visit_sec", 0) + r.get("wait_sec", 0) for r in route_summaries)
            _n_rt = len(route_summaries)
            _time_total = total_duration + total_visit
            stat_strip([
                {"icon": "🧭", "label": "Total Rute", "value": _n_rt,
                 "sub": f"≈ {round(result['total_points'] / _n_rt)} titik per rute" if _n_rt > 1 else None},
                {"icon": "📍", "label": "Total Titik", "value": result["total_points"], "sub": "merchant terjadwal"},
                {"icon": "📏", "label": "Estimasi Total Jarak", "value": f"{total_distance:.1f}", "unit": "km",
                 "sub": f"≈ {total_distance / _n_rt:.1f} km per rute" if _n_rt > 1 else None},
                {"icon": "⏱️", "label": "Waktu Total" if total_visit else "Estimasi Waktu Tempuh",
                 "value": format_duration_short(_time_total),
                 "sub": ("jalan + kunjungan + tunggu" if total_visit
                         else (f"≈ {format_duration_short(_time_total / _n_rt)} per rute" if _n_rt > 1 else "waktu di jalan"))},
            ])

            _tf = st.session_state.pop("territory_flash", None)
            if _tf:
                st.toast(_tf)
            _sched = build_schedule_matrix(route_summaries)
            if _sched is not None:
                with st.container(border=True):
                    st.markdown("**📅 Jadwal petugas**")
                    st.dataframe(_sched, width="stretch")
            _tn_km = sum(r.get("naive_distance_km", r["distance_km"]) for r in route_summaries)
            if _tn_km > 0 and len(df) >= 3 and _tn_km - total_distance > 0.05:
                st.info(
                    f"**Hemat {_tn_km - total_distance:.1f} km ({(_tn_km - total_distance) / _tn_km * 100:.0f}%)** "
                    f"dibanding sebelum optimasi: {_tn_km:.1f} km → {total_distance:.1f} km.",
                    icon="📉",
                )

            section_header(
                "3️⃣", "Hasil Rute",
                "Unduh atau bagikan langsung, lalu lihat detail, peta, dan perbandingannya di bawah",
            )
            with st.container(border=True):
                st.markdown("**📥 Unduh**" + (" — Excel dan PDF siap cetak" if IS_PRO else " — Excel berisi semua rute"))
                if IS_PRO:
                    dl1, dl2 = st.columns(2)
                else:
                    dl1, dl2 = st.container(), None
                with dl1:
                    # Dibangun ulang di sini (bukan pakai result["excel_bytes"] yang
                    # dicache saat generate) supaya nama petugas yang baru diisi ikut
                    # terbawa — kolom "petugas" dibaca langsung dari r["driver"].
                    st.download_button(
                        label="📥 Excel (semua rute)",
                        data=build_excel_bytes(route_summaries),
                        file_name="hasil_routing.xlsx",
                        mime="application/vnd.ms-excel",
                        type="primary",
                        width='stretch',
                        on_click=_mark_routes_saved,
                    )
                if IS_PRO:
                    with dl2:
                        if PDF_OK:
                            all_payloads = []
                            for _r in route_summaries:
                                _links, _seq, _ = route_links_info(_r, MAPS_MAX_WAYPOINTS_DESKTOP)
                                all_payloads.append(_pdf_payload(_r, _links, _seq, result))
                            st.download_button(
                                label="🖨️ PDF semua rute (1 rute/halaman)",
                                data=_routes_pdf_cached(all_payloads),
                                file_name="lembar_rute_semua.pdf",
                                mime="application/pdf",
                                width='stretch',
                                on_click=_mark_routes_saved,
                            )
                        else:
                            st.caption("PDF belum tersedia: pustaka `reportlab` belum terpasang di server.")

                st.markdown("**📲 Kirim via WhatsApp** — satu pesan ringkas berisi semua rute")
                _all_wa_parts = []
                for _r in route_summaries:
                    _links, _, _ = route_links_info(_r, MAPS_MAX_WAYPOINTS_DESKTOP)
                    _all_wa_parts.append(build_whatsapp_text(_r, _links))
                wa_text_all = (
                    f"*Ringkasan {len(route_summaries)} Rute*\n\n"
                    + ("\n\n" + "━" * 20 + "\n\n").join(_all_wa_parts)
                )
                wa_url_all = "https://wa.me/?text=" + quote(wa_text_all, safe="")
                if len(wa_url_all) <= 3800:
                    st.link_button(
                        "📲 Kirim Semua Rute via WhatsApp", wa_url_all, type="primary", width='stretch'
                    )
                else:
                    st.caption(
                        f"ℹ️ Teks gabungan {len(route_summaries)} rute ini terlalu panjang untuk tombol "
                        "WhatsApp langsung. Salin manual lewat tombol di bawah, atau kirim tiap rute "
                        "terpisah lewat tombol WhatsApp di masing-masing rute di atas (lebih aman untuk "
                        "rute dengan banyak titik)."
                    )
                with st.popover("📋 Salin teks semua rute"):
                    st.code(wa_text_all, language=None)
                _step_all = (
                    f"*Ringkasan {len(route_summaries)} Rute · navigasi titik demi titik*\n\n"
                    + ("\n\n" + "━" * 20 + "\n\n").join(build_stepwise_text(_r) for _r in route_summaries)
                )
                _step_all_wa = "https://wa.me/?text=" + quote(_step_all, safe="")
                st.markdown("**🧭 Navigasi titik demi titik** — tiap merchant punya tautan navigasi sendiri")
                if len(_step_all_wa) <= 3800:
                    st.link_button("📲 Kirim Semua Rute via WhatsApp (titik demi titik)", _step_all_wa, width='stretch')
                else:
                    st.caption("ℹ️ Teks gabungan terlalu panjang untuk tombol WhatsApp langsung. Salin lewat tombol di bawah, "
                               "atau kirim per rute dari bagian 🧭 di masing-masing rute.")
                with st.popover("📋 Salin teks semua rute (titik demi titik)"):
                    st.code(_step_all, language=None)

            _views = ["🛣️ Detail rute"] + (["🗺️ Peta semua rute"] if len(route_summaries) >= 2 else []) + ["📱 Mode Lapangan", "📊 Ringkasan & perbandingan"]
            if st.session_state.get("_result_view") not in _views:
                st.session_state["_result_view"] = _views[0]
            with st.container(key="resultview"):
                _view = st.radio("Tampilan hasil", _views, key="_result_view", horizontal=True, label_visibility="collapsed")
            if _view == _views[0]:
                _pf = "Semua"
                if any(r.get("petugas") for r in route_summaries):
                    _pnames = list(dict.fromkeys(r["petugas"] for r in route_summaries))
                    _pf = st.selectbox("Tampilkan petugas", ["Semua"] + _pnames, key="_dp_filter")
                _rq, _only_check = "", False
                if len(route_summaries) >= 2:   # lebih dari 1 rute: beri jalan pintas untuk menemukan merchant / rute tertentu
                    _fc1, _fc2 = st.columns([3, 2])
                    with _fc1:
                        _rq = st.text_input(
                            "🔎 Cari merchant, petugas, atau nomor rute", key="_route_q",
                            placeholder="mis. Toko Maju, Budi, atau 3",
                        )
                    with _fc2:
                        if any(route_needs_check(x) for x in route_summaries):
                            _only_check = st.checkbox(
                                "Hanya rute yang perlu dicek", key="_route_only_check",
                                help="Rute yang memakai estimasi garis lurus (⚠️) atau punya kunjungan di luar jam operasional.",
                            )
                _by_text, _by_number = search_routes(route_summaries, _rq)
                _visible = [
                    x for x in _by_text
                    if (_pf == "Semua" or x.get("petugas") == _pf)
                    and (not _only_check or route_needs_check(x))
                ]
                if len(_visible) < len(route_summaries):
                    st.caption(f"Menampilkan {len(_visible)} dari {len(route_summaries)} rute.")
                if _rq.strip() and not _by_number:
                    _hits, _n_hits = find_merchant_hits(route_summaries, _rq)
                    if _hits:
                        st.caption(
                            "📍 " + " · ".join(
                                f"{_md_escape(_nm)} → Rute {_rn}" + (f" (urutan {_sq})" if _sq else "")
                                for _nm, _rn, _sq in _hits
                            ) + (f" · +{_n_hits - len(_hits)} lagi" if _n_hits > len(_hits) else "")
                        )
                if not _visible:
                    st.info("Tidak ada rute yang cocok dengan pencarian atau filter ini.")
                # Buka otomatis: hasil pencarian yang sedikit (≤3), selain itu rute pertama yang tampil.
                if _rq.strip() and 0 < len(_visible) <= 3:
                    _open_ids = {x["route_id"] for x in _visible}
                else:
                    _open_ids = {_visible[0]["route_id"]} if _visible else set()
                for r in _visible:
                    route_id = r["route_id"]
                    optimized_df = r["df"]
                    color = ROUTE_COLORS[route_id % len(ROUTE_COLORS)]
                    emoji = ROUTE_EMOJIS[route_id % len(ROUTE_EMOJIS)]

                    route_total_sec = r["duration_sec"] + r.get("visit_sec", 0) + r.get("wait_sec", 0)
                    with st.expander(
                        route_title(r, emoji),
                        # tetap terbuka saat sedang diedit (judulnya berubah tiap urutan digeser)
                        expanded=(route_id in _open_ids) or bool(st.session_state.get(f"edit_{route_id}", False)),
                    ):
                        parts = [f"🚗 Perjalanan {format_duration(r['duration_sec'])}"]
                        if not r.get("real_roads", True):
                            parts.append("⚠️ Estimasi garis lurus (bukan jalan sebenarnya)")
                        if r.get("manual"):
                            parts.append("✏️ Urutan diubah manual")
                        if r.get("visit_sec"):
                            parts.append(f"🏪 Kunjungan {format_duration(r['visit_sec'])}")
                        if r.get("wait_sec", 0) >= 60:
                            parts.append(f"⏳ Menunggu toko buka {format_duration(r['wait_sec'])}")
                        if r.get("finish_label"):
                            parts.append(
                                f"🏁 Selesai ±{r['finish_label']}"
                                + (" (sudah termasuk pulang)" if r.get("round_trip") else "")
                            )
                        if r.get("depot_name"):
                            parts.append(f"🏭 Titik awal: {r['depot_name']}")
                        _route_saved = r.get("naive_distance_km", r["distance_km"]) - r["distance_km"]
                        if _route_saved > 0.05:
                            parts.append(f"📉 Hemat {_route_saved:.1f} km vs sebelum optimasi")
                        st.caption(" · ".join(parts))
                        if r.get("n_outside_hours"):
                            st.warning(
                                f"⚠️ {r['n_outside_hours']} merchant diperkirakan dikunjungi di luar jam "
                                "operasional (lihat kolom status di tabel / Catatan di PDF)."
                            )

                        if IS_PRO:
                            driver_val = st.text_input(
                                "🧑‍✈️ Nama petugas (opsional)",
                                value=st.session_state.driver_names.get(route_id, ""),
                                key=f"driver_{route_id}",
                                placeholder="Mis. Budi",
                            )
                            st.session_state.driver_names[route_id] = driver_val
                            r["driver"] = driver_val

                        left, right = st.columns([1, 1.4])
                        with left:
                            map_links, seq_nums, link_df = route_links_info(r, MAPS_MAX_WAYPOINTS_DESKTOP)
                            _display_cols = ["sequence", "merchant_name"]
                            _display_cols += [c for c in ("jam_tiba", "jam_selesai") if c in optimized_df.columns]
                            _show_df = optimized_df[_display_cols + ["latitude", "longitude"]].copy()
                            if "prioritas_flag" in optimized_df.columns:
                                _show_df.insert(2, "⭐ Prioritas", optimized_df["prioritas_flag"].map({True: "⭐ Ya", False: ""}))
                            if "jadwal_status" in optimized_df.columns:
                                _show_df["Status Jam"] = optimized_df["jadwal_status"]

                            _table_obj = _show_df
                            if len(map_links) > 1:
                                # Rute dibagi jadi beberapa link Google Maps: tandai tiap baris masuk bagian mana.
                                _part_labels, _part_tints = maps_part_labels(map_links, len(_show_df))
                                _show_df.insert(1, "Bagian Maps", _part_labels)
                                _tint_by_idx = dict(zip(_show_df.index, _part_tints))
                                try:
                                    _table_obj = _show_df.style.apply(
                                        lambda row: [f"background-color: {_tint_by_idx[row.name]}"] * len(row), axis=1
                                    )
                                except Exception:
                                    _table_obj = _show_df  # tanpa pewarnaan kalau Styler tak tersedia
                            st.dataframe(
                                _table_obj,
                                width='stretch',
                                **TABLE_KW,
                                hide_index=True,
                            )
                            if len(map_links) > 1:
                                st.caption(
                                    "🧭 Kolom **Bagian Maps** menunjukkan merchant ini masuk link Google Maps yang mana "
                                    "(mis. 1/3 = link pertama dari 3). "
                                    + ("Tiap bagian dimulai dari lokasi Anda saat link-nya dibuka." if r.get("from_my_location")
                                       else "Baris **abu-abu** dengan dua bagian adalah titik sambungan: tujuan bagian sebelumnya "
                                            "sekaligus titik awal bagian berikutnya.")
                                )
                            if IS_PRO and st.checkbox(
                                "✏️ Ubah urutan manual", key=f"edit_{route_id}",
                                help="Geser merchant naik/turun, misalnya karena toko tutup jam tertentu atau ada janji. "
                                     "Jarak, jam tiba, peta, Excel, WhatsApp, dan PDF ikut diperbarui."
                            ):
                                render_reorder_controls(r)
                            # Batas 9 titik singgah berlaku untuk aplikasi Google Maps (Android/iOS)
                            # MAUPUN desktop — dan tap link di HP hampir selalu membuka aplikasi
                            # tersebut (deep-link), bukan browser HP. Batas 3 titik singgah menurut
                            # Google hanya berlaku kalau link dibuka di BROWSER HP secara spesifik,
                            # jadi kita pakai 9 sebagai default supaya tidak kepecah link-nya tanpa
                            # alasan untuk kasus paling umum, dan cukup beri catatan untuk skenario
                            # browser-HP yang lebih jarang terjadi.
                            max_wp = MAPS_MAX_WAYPOINTS_DESKTOP
                            _mine = bool(r.get("from_my_location"))
                            link_waypoints = max(0, len(link_df) - ((2 if r.get("has_start") else 1) if _mine else 2))
                            if _mine:
                                st.caption(
                                    "📍 Tiap link rute ini dimulai dari **lokasi Anda saat link dibuka** (Google Maps memakai GPS perangkat)."
                                    + (" Titik awal rute hanya dipakai untuk menyusun urutan; "
                                       + ("pulang ke titik awal ikut sebagai tujuan terakhir." if r.get("round_trip") else "tidak ikut di link.")
                                       if r.get("has_start") else
                                       (" Perjalanan pulang ke lokasi awal tidak ikut di link; navigasikan manual." if r.get("round_trip") else ""))
                                )
                            if len(map_links) == 1:
                                st.link_button("🚗 Buka di Google Maps", map_links[0][2], width='stretch')
                                if IS_MOBILE and link_waypoints > MAPS_MAX_WAYPOINTS_MOBILE:
                                    st.caption(
                                        "ℹ️ Kalau link ini dibuka di **browser HP** (bukan aplikasi Google "
                                        f"Maps), Google Maps mungkin hanya menampilkan {MAPS_MAX_WAYPOINTS_MOBILE} "
                                        "titik singgah pertama. Buka lewat aplikasi Google Maps untuk rute lengkap."
                                    )
                            elif len(map_links) > 1:
                                st.caption(
                                    f"ℹ️ Google Maps membatasi titik singgah (maks. {max_wp} per link), "
                                    f"jadi rute dibagi jadi {len(map_links)} link. Buka berurutan — "
                                    + ("tiap bagian dimulai dari lokasi Anda saat link-nya dibuka (buka bagian berikutnya setelah "
                                       "selesai dengan bagian sebelumnya)." if r.get("from_my_location")
                                       else "tiap bagian dimulai dari titik akhir bagian sebelumnya.")
                                )
                                for i, (ia, ib, url) in enumerate(map_links, start=1):
                                    st.link_button(
                                        f"{MAPS_PART_EMOJIS[(i - 1) % len(MAPS_PART_EMOJIS)]} 🚗 Bagian {i}/{len(map_links)} · titik {seq_nums[ia]} → {seq_nums[ib]}",
                                        url,
                                        width='stretch',
                                    )

                            with st.popover("🧭 Navigasi titik demi titik (cadangan)"):
                                st.caption(
                                    "Kalau navigasi multi-titik Google Maps berhenti di titik singgah (\"sudah sampai tujuan\"), "
                                    "pakai tombol di bawah: tiap tombol memulai navigasi dari **lokasi Anda saat ini** ke satu "
                                    "titik. Setelah tiba, tekan tombol titik berikutnya."
                                )
                                _step_text = build_stepwise_text(r)
                                _step_wa = "https://wa.me/?text=" + quote(_step_text, safe="")
                                if len(_step_wa) <= 3800:
                                    st.link_button("📲 Kirim via WhatsApp (titik demi titik)", _step_wa, width='stretch')
                                else:
                                    st.caption(
                                        "ℹ️ Teks rute terlalu panjang untuk tombol langsung — "
                                        "salin lewat pilihan di bawah lalu tempel di WhatsApp."
                                    )
                                if st.checkbox("📋 Salin teks rute (titik demi titik)", key=f"stepcopy_{route_id}"):
                                    with st.container(height=200):     # kotak bergulir: teks panjang tidak memanjangkan halaman
                                        st.code(_step_text, language=None)
                                _first_stop = 1 if r.get("has_start") else 0            # titik awal tetap bukan tujuan kunjungan
                                _stops = r["df"].iloc[_first_stop:]
                                _sel_key = f"stepsel_{route_id}"
                                if len(_stops):
                                    _pick = st.selectbox(
                                        f"Titik tujuan ({len(_stops)} titik) — ketik untuk mencari",
                                        options=list(range(len(_stops))),
                                        format_func=lambda i, _s=_stops: f"{int(_s.iloc[i]['sequence'])}. {_s.iloc[i]['merchant_name']}",
                                        key=_sel_key,
                                    )
                                    _row = _stops.iloc[_pick]
                                    st.link_button(
                                        f"🧭 Navigasi ke titik {int(_row['sequence'])}",
                                        stop_nav_url(_row["latitude"], _row["longitude"]),
                                        type="primary", width='stretch',
                                    )
                                    st.button(
                                        "⏭️ Titik berikutnya", key=f"stepnext_{route_id}", width='stretch',
                                        on_click=_step_next, args=(_sel_key, len(_stops)),
                                        disabled=_pick >= len(_stops) - 1,
                                    )
                            wa_text = build_whatsapp_text(r, map_links)
                            wa_url = "https://wa.me/?text=" + quote(wa_text, safe="")
                            if len(wa_url) <= 3800:
                                st.link_button("📲 Kirim via WhatsApp", wa_url, width='stretch')
                            else:
                                st.caption(
                                    "ℹ️ Teks rute terlalu panjang untuk tombol langsung — "
                                    "salin lewat tombol di bawah lalu tempel di WhatsApp."
                                )
                            with st.popover("📋 Salin teks rute"):
                                st.code(wa_text, language=None)
                            if IS_PRO and PDF_OK:
                                st.download_button(
                                    "🖨️ Unduh PDF (siap cetak)",
                                    data=_routes_pdf_cached([_pdf_payload(r, map_links, seq_nums, result)]),
                                    file_name=f"lembar_rute_{route_id + 1}.pdf",
                                    mime="application/pdf",
                                    key=f"pdf_{route_id}",
                                    width='stretch',
                                )

                        with right:
                            center_lat = optimized_df["latitude"].mean()
                            center_lon = optimized_df["longitude"].mean()
                            fmap = folium.Map(location=[center_lat, center_lon], zoom_start=12)
                            polyline_coords = []
                            for idx, row in optimized_df.iterrows():
                                coord = [row["latitude"], row["longitude"]]
                                polyline_coords.append(coord)
                                is_start_pt = bool(r.get("has_start")) and idx == 0
                                folium.Marker(
                                    coord,
                                    popup=f"{idx + 1}. {row['merchant_name']}",
                                    tooltip=f"{'Titik awal' if is_start_pt else idx + 1} · {row['merchant_name']}",
                                    icon=numbered_icon("S" if is_start_pt else idx + 1, color, is_start_pt),
                                ).add_to(fmap)
                            if r.get("round_trip") and polyline_coords:
                                polyline_coords.append(polyline_coords[0])
                            folium.PolyLine(polyline_coords, weight=4, color=color).add_to(fmap)
                            st_folium(fmap, width=None, height=MAP_H, key=f"map_{route_id}", returned_objects=[])

            elif _view.startswith("📱"):
                render_field_mode(route_summaries, result)

            elif _view.startswith("🗺️"):
                st_folium(
                    build_combined_map(route_summaries), width=None, height=COMBINED_MAP_H,
                    key="map_all", returned_objects=[],
                )

            else:
                _sum_rows = [
                    {
                        "Rute": f"Rute {r['route_id'] + 1}" + (f" — {r['driver']}" if r.get("driver") else ""),
                        "Tanggal": fmt_day_label(datetime.date.fromisoformat(r["tanggal"])) if r.get("tanggal") else "",
                        "Titik": len(r["df"]),
                        "Jarak (km)": round(r["distance_km"], 1),
                        "Waktu total": format_duration(r["duration_sec"] + r.get("visit_sec", 0) + r.get("wait_sec", 0)),
                    }
                    for r in route_summaries
                ]
                if not any(x["Tanggal"] for x in _sum_rows):
                    for x in _sum_rows:
                        x.pop("Tanggal", None)
                st.dataframe(pd.DataFrame(_sum_rows), width="stretch", hide_index=True)
                if result.get("day_plan"):
                    _assign = {}
                    for _r in route_summaries:
                        for _, _row in _r["df"].iterrows():
                            _key = st.session_state.row_key_map.get(_row_sig(_row["merchant_name"], _row["latitude"], _row["longitude"]))
                            if _key:
                                _assign[_key] = _r["petugas"]
                    st.button(
                        "🔒 Simpan wilayah petugas ke data", key="_save_terr", on_click=_save_territories, args=(_assign,),
                        help="Menyimpan siapa memegang merchant mana ke kolom petugas. Aktifkan 'Kunci wilayah petugas' "
                             "supaya pembagian berikutnya tetap memakai wilayah ini (merchant baru ikut area terdekat).",
                    )
                    st.caption("Wilayah tersimpan ikut ke **Lihat & Edit Data Awal**, unduhan data hasil edit, dan Simpan/Buka Sesi.")
                # Perbandingan dengan mengunjungi merchant sesuai urutan di file (tanpa optimasi).
                total_naive_km = sum(r.get("naive_distance_km", r["distance_km"]) for r in route_summaries)
                total_naive_sec = sum(r.get("naive_duration_sec", r["duration_sec"]) for r in route_summaries)
                delta_km = total_naive_km - total_distance
                delta_sec = total_naive_sec - total_duration
                if total_naive_km > 0 and len(df) >= 3:
                    section_header(
                        "📉", "Sebelum vs Sesudah Optimasi",
                        "Sebelum optimasi = mengunjungi merchant sesuai urutan di file kamu",
                    )
                    saving_pct = delta_km / total_naive_km * 100
                    compare_panel(total_naive_km, total_distance, delta_km, saving_pct)
                    if delta_km > 0.05:
                        st.caption(
                            f"💡 Hemat ±{format_duration(max(delta_sec, 0))} waktu perjalanan dibanding sebelum optimasi "
                            "(belum termasuk waktu kunjungan)."
                        )
                    elif delta_km < -0.05:
                        st.caption(
                            f"ℹ️ Rute sekarang {abs(delta_km):.1f} km lebih panjang dibanding sebelum optimasi — biasanya karena "
                            "merchant prioritas diutamakan atau urutan diubah manual."
                        )
                    else:
                        st.caption("ℹ️ Urutan awal (sebelum optimasi) ternyata sudah hampir seefisien hasil optimasi.")

        elif result and result["fingerprint"] != data_fingerprint:
            st.info("ℹ️ Pengaturan atau data berubah — tekan **Buat Rute Optimal Sekarang** lagi untuk memperbarui hasil.")
    else:
        empty_state(
            "📂",
            "Belum ada data untuk diproses",
            "Upload file Excel/CSV di atas, atau centang opsi data dari Maps Extractor untuk mulai membuat rute optimal.",
        )

# ================================================================
# HALAMAN 2: MAPS EXTRACTOR
# ================================================================
elif st.session_state.page == "Kobo":
    render_hero(
        "Kunjungan lapangan", "Survey", "Form",
        "Buat formulir KoboCollect dari data merchant, lalu ambil hasil kunjungan petugas langsung dari KoboToolbox.",
    )
    render_kobo_page()
elif st.session_state.page == "Extract":
    render_hero(
        "Ekstraksi lokasi", "Maps", "Extractor",
        "Ubah link Google Maps, pencarian nama merchant (lewat OpenStreetMap), atau input manual jadi tabel (merchant_name, latitude, longitude) siap pakai.",
    )

    tab_link, tab_search, tab_manual = st.tabs(
        ["🔗 Link", "🔎 Cari", "✏️ Manual"] if IS_MOBILE
        else ["🔗 Dari Link Google Maps", "🔎 Cari Nama Merchant", "✏️ Input Manual"]
    )

    with tab_link:
        with st.form("extractor_form", clear_on_submit=True):
            new_link = st.text_input("Paste link Google Maps di sini:")
            submitted = st.form_submit_button("➕ Ekstrak & Tambahkan Data", type="primary", width='stretch')

            if submitted:
                if not new_link.strip():
                    st.error("❌ Link tidak boleh kosong.")
                else:
                    with fancy_loading("Membaca link Google Maps", "Mengambil nama dan koordinat lokasi"):
                        name, lat, lon = extract_google_maps_data(new_link)

                    if lat is not None and lon is not None:
                        # Give every entry with an unrecognized name a unique
                        # placeholder — never reuse one fixed label, or every
                        # unparsed entry ends up looking like the same
                        # "duplicate" merchant on the map.
                        if not name:
                            name = f"Lokasi {len(st.session_state.extracted_data) + 1}"
                            st.warning(
                                f"Nama merchant tidak terdeteksi dari link — diberi nama sementara "
                                f"**{name}**. Silakan edit di tabel di bawah."
                            )

                        is_duplicate = any(
                            abs(d["latitude"] - lat) < 1e-5 and abs(d["longitude"] - lon) < 1e-5
                            for d in st.session_state.extracted_data
                        )

                        st.session_state.extracted_data.append(
                            {"merchant_name": name, "latitude": float(lat), "longitude": float(lon)}
                        )
                        st.success(f"✅ Berhasil menambahkan: {name}")
                        if is_duplicate:
                            st.warning(
                                "⚠️ Koordinat ini sama persis dengan data lain yang sudah ada — "
                                "periksa apakah link-nya benar-benar berbeda."
                            )
                    else:
                        st.error(
                            "❌ Gagal mendeteksi koordinat dari link tersebut. Pastikan link berasal "
                            "dari halaman detail lokasi di Google Maps (bukan link pencarian), lalu "
                            "gunakan tombol **Bagikan → Salin link**."
                        )

    with tab_search:
        st.info(
            "Pencarian gratis via OpenStreetMap — tanpa API key, tapi cakupan merchant kecil/UMKM "
            "di Indonesia masih lebih terbatas dibanding Google Maps. Sertakan kota/wilayah supaya "
            "hasilnya lebih akurat.",
            icon="💡",
        )
        sc1, sc2 = st.columns([2, 1])
        with sc1:
            search_query = st.text_input(
                "Nama merchant", key="nominatim_query", placeholder="contoh: Warung Bu Tini"
            )
        with sc2:
            search_city = st.text_input(
                "Kota/wilayah (opsional)", key="nominatim_city", placeholder="contoh: Surakarta"
            )

        if st.button("🔍 Cari Lokasi", type="primary", width='stretch'):
            if not search_query.strip():
                st.error("❌ Nama merchant tidak boleh kosong.")
            else:
                full_query = (
                    f"{search_query.strip()}, {search_city.strip()}"
                    if search_city.strip()
                    else search_query.strip()
                )
                with fancy_loading("Mencari lokasi", "Menelusuri OpenStreetMap"):
                    results, search_error = search_nominatim(full_query)
                st.session_state.nominatim_results = results
                st.session_state.nominatim_searched_for = full_query
                st.session_state.nominatim_query_name = search_query.strip()
                st.session_state.pop("nominatim_selected_idx", None)
                if search_error:
                    st.error(f"⚠️ {search_error}")
                elif not results:
                    st.warning(
                        "Tidak ditemukan hasil. Coba nama yang lebih spesifik, tambahkan "
                        "kota/wilayah, atau gunakan tab **Dari Link Google Maps** sebagai alternatif "
                        "yang cakupannya lebih luas."
                    )

        results = st.session_state.get("nominatim_results", [])
        if results:
            st.markdown(
                f"**🔎 Ditemukan {len(results)} hasil untuk:** _{st.session_state.get('nominatim_searched_for', '')}_"
            )
            idx_selected = st.radio(
                "Pilih lokasi yang paling sesuai:",
                options=list(range(len(results))),
                format_func=lambda i: results[i].get("display_name", "(tanpa nama)"),
                key="nominatim_selected_idx",
            )

            if st.button("➕ Tambahkan Lokasi Terpilih", type="primary", width='stretch'):
                chosen = results[idx_selected]
                try:
                    lat = float(chosen["lat"])
                    lon = float(chosen["lon"])
                except (KeyError, ValueError, TypeError):
                    st.error("❌ Data koordinat dari hasil pencarian tidak valid.")
                else:
                    name = nominatim_result_name(
                        chosen, fallback_query=st.session_state.get("nominatim_query_name", "")
                    )
                    is_duplicate = any(
                        abs(d["latitude"] - lat) < 1e-5 and abs(d["longitude"] - lon) < 1e-5
                        for d in st.session_state.extracted_data
                    )
                    st.session_state.extracted_data.append(
                        {"merchant_name": name, "latitude": lat, "longitude": lon}
                    )
                    st.success(f"✅ Berhasil menambahkan: {name}")
                    if is_duplicate:
                        st.warning(
                            "⚠️ Koordinat ini sama persis dengan data lain yang sudah ada — "
                            "periksa apakah lokasinya benar-benar berbeda."
                        )

    with tab_manual:
        with st.form("manual_form", clear_on_submit=True):
            manual_name = st.text_input("Nama merchant", placeholder="contoh: Toko Berkah")
            manual_coord = st.text_input(
                "📋 Tempel koordinat",
                placeholder="-7.5665, 110.8167",
                help=(
                    "Di Google Maps: klik kanan (atau tekan lama di HP) pada lokasi, lalu klik/sentuh angka "
                    "koordinat di bagian atas menu untuk menyalinnya, dan tempel di sini."
                ),
            )
            with st.expander("Atau isi latitude & longitude secara terpisah"):
                mc2, mc3 = st.columns(2)
                with mc2:
                    manual_lat = st.number_input(
                        "Latitude", value=0.0, format="%.6f",
                        help="Gunakan titik desimal, contoh: -7.5665",
                    )
                with mc3:
                    manual_lon = st.number_input(
                        "Longitude", value=0.0, format="%.6f",
                        help="Gunakan titik desimal, contoh: 110.8167",
                    )
            manual_submit = st.form_submit_button("➕ Tambahkan Data", type="primary", width='stretch')

            if manual_submit:
                lat = lon = None
                if not manual_name.strip():
                    st.error("❌ Nama merchant tidak boleh kosong.")
                elif manual_coord.strip():
                    lat, lon, coord_err = parse_coordinate_text(manual_coord)
                    if coord_err:
                        st.error(f"❌ {coord_err}")
                elif manual_lat == 0.0 and manual_lon == 0.0:
                    st.error("❌ Isi koordinat: tempel di kolom koordinat, atau isi latitude & longitude.")
                else:
                    lat, lon = manual_lat, manual_lon

                if lat is not None and lon is not None:
                    st.session_state.extracted_data.append(
                        {"merchant_name": manual_name.strip(), "latitude": float(lat), "longitude": float(lon)}
                    )
                    st.success(f"✅ Berhasil menambahkan: {manual_name.strip()}")

    if len(st.session_state.extracted_data) > 0:
        section_header(
            "📋", "Data yang Sudah Dikumpulkan",
            f"{len(st.session_state.extracted_data)} lokasi — klik dua kali sel untuk edit, atau hapus baris yang tidak perlu",
        )

        df_extract = pd.DataFrame(st.session_state.extracted_data)
        edited_df = st.data_editor(
            df_extract,
            width='stretch',
            num_rows="dynamic",
            **TABLE_KW,
            key=_wk("extract_editor"),
            column_config={
                "latitude": st.column_config.NumberColumn(format="%.6f"),
                "longitude": st.column_config.NumberColumn(format="%.6f"),
            },
        )
        st.session_state.extracted_data = edited_df.to_dict("records")

        with st.expander("🗺️ Lihat lokasi di peta"):
            valid_points = edited_df.dropna(subset=["latitude", "longitude"])
            if not valid_points.empty:
                fmap = folium.Map(
                    location=[valid_points["latitude"].mean(), valid_points["longitude"].mean()],
                    zoom_start=12,
                )
                for _, row in valid_points.iterrows():
                    folium.Marker([row["latitude"], row["longitude"]], popup=row["merchant_name"]).add_to(fmap)
                st_folium(fmap, width=None, height=MAP_H, key="extract_map", returned_objects=[])

        col1, col2, col3 = st.columns([1, 1, 1.3])
        with col1:
            if st.button("🗑️ Hapus Semua", width='stretch'):
                st.session_state.extracted_data = []
                st.rerun()
        with col2:
            buffer_ext = io.BytesIO()
            with pd.ExcelWriter(buffer_ext, engine="openpyxl") as writer:
                edited_df.to_excel(writer, index=False)
            st.download_button(
                label="📥 Download Excel",
                data=buffer_ext.getvalue(),
                file_name="hasil_extract_gmaps.xlsx",
                mime="application/vnd.ms-excel",
                width='stretch',
            )
        with col3:
            if st.button("➡️ Pakai di Routing Optimizer", type="primary", width='stretch'):
                st.session_state.use_extracted_flag = True
                st.session_state.page = "Routing"
                st.rerun()
    else:
        empty_state(
            "🗺️",
            "Belum ada lokasi yang dikumpulkan",
            "Tempel link Google Maps, cari nama merchant, atau isi manual lewat tab di atas untuk mulai mengumpulkan data.",
        )


autosave_session()
render_persist_caption(_persist_slot)         # status simpan otomatis terbaru (setelah autosave di akhir run)
render_unsaved_notice(_notice_slot, IS_PRO)   # hitung ulang: hasil/edit yang baru dibuat di run ini
render_footer()
