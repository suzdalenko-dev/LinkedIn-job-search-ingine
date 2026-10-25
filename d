[33mcommit ebde042806c8c8bec3a14755e7008085a669ce3a[m
Author: suzdalenko-dev <alexey.saron@gmail.com>
Date:   Sun Oct 25 00:13:13 2026 +0200

    suzdsalenko

[1mdiff --git a/html/login.html b/html/login.html[m
[1mindex c417b25..3bf9308 100644[m
[1m--- a/html/login.html[m
[1m+++ b/html/login.html[m
[36m@@ -11,9 +11,7 @@[m
 [m
 <body>[m
     <header class="topbar">[m
[31m-        <a href="#" class="logo" aria-label="Demo Empleo inicio">[m
[31m-            Linked<span>On</span>[m
[31m-        </a>[m
[32m+[m[32m        <a class="brand" href="#inicio" aria-label="Inicio">Linked<span>On</span></a>[m
         <span class="demo-label">SIMULACIÓN LOCAL</span>[m
     </header>[m
 [m
[36m@@ -457,6 +455,20 @@[m
                 font-size: 28px;[m
             }[m
         }[m
[32m+[m[32m        .brand {[m
[32m+[m[32m            font-size: 26px;[m
[32m+[m[32m            font-weight: 555;[m
[32m+[m[32m            letter-spacing: -1.5px;[m
[32m+[m[32m            color: var(--blue);[m
[32m+[m[32m            white-space: nowrap[m
[32m+[m[32m        }[m
[32m+[m
[32m+[m[32m        .brand span {[m
[32m+[m[32m            background: var(--blue);[m
[32m+[m[32m            color: #fff;[m
[32m+[m[32m            border-radius: 3px;[m
[32m+[m[32m            padding: 0 3px[m
[32m+[m[32m        }[m
     </style>[m
     <script>[m
 [m
[1mdiff --git a/html/offers.html b/html/offers.html[m
[1mindex 1c48f12..271fce2 100644[m
[1m--- a/html/offers.html[m
[1m+++ b/html/offers.html[m
[36m@@ -64,19 +64,6 @@[m
             gap: 10px[m
         }[m
 [m
[31m-        .brand {[m
[31m-            display: flex;[m
[31m-            align-items: center;[m
[31m-            justify-content: center;[m
[31m-            width: 218px;[m
[31m-            height: 28px;[m
[31m-            background: var(--blue);[m
[31m-            color: #fff;[m
[31m-            border-radius: 3px;[m
[31m-            font-size: 22px;[m
[31m-            font-weight: 750;[m
[31m-            letter-spacing: -1px[m
[31m-        }[m
 [m
         .search {[m
             height: 32px;[m
[36m@@ -615,6 +602,20 @@[m
                 padding: 0 8px[m
             }[m
         }[m
[32m+[m[32m        .brand {[m
[32m+[m[32m            font-size: 26px;[m
[32m+[m[32m            font-weight: 555;[m
[32m+[m[32m            letter-spacing: -1.5px;[m
[32m+[m[32m            color: var(--blue);[m
[32m+[m[32m            white-space: nowrap[m
[32m+[m[32m        }[m
[32m+[m
[32m+[m[32m        .brand span {[m
[32m+[m[32m            background: var(--blue);[m
[32m+[m[32m            color: #fff;[m
[32m+[m[32m            border-radius: 3px;[m
[32m+[m[32m            padding: 0 3px[m
[32m+[m[32m        }[m
     </style>[m
 </head>[m
 [m
[1mdiff --git a/html/profile.html b/html/profile.html[m
[1mindex bd12f2c..b8aa201 100644[m
[1m--- a/html/profile.html[m
[1m+++ b/html/profile.html[m
[36m@@ -61,13 +61,13 @@[m
 [m
         .brand {[m
             font-size: 26px;[m
[31m-            font-weight: 750;[m
[32m+[m[32m            font-weight: 555;[m
             letter-spacing: -1.5px;[m
             color: var(--blue);[m
             white-space: nowrap[m
         }[m
 [m
[31m-        .brand b {[m
[32m+[m[32m        .brand span {[m
             background: var(--blue);[m
             color: #fff;[m
             border-radius: 3px;[m
[36m@@ -707,7 +707,7 @@[m
 <body>[m
     <header class="top">[m
         <nav class="nav" aria-label="Navegación principal">[m
[31m-            <a class="brand" href="#inicio" aria-label="Inicio">Linked<b>On</b></a>[m
[32m+[m[32m            <a class="brand" href="#inicio" aria-label="Inicio">Linked<span>On</span></a>[m
             <div class="searchbox"><input class="search" id="search" placeholder="Buscar"[m
                     aria-label="Buscar en la demostración"></div>[m
             <div class="navitems">[m
