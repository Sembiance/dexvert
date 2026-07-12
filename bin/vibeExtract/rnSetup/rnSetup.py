#!/usr/bin/env python3
# Vibe coded by Codex
"""Extract RealNetworks RNSetup resource archives."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import struct
import sys
import tempfile
import zlib


CODEC_B85 = (
    b"c-ri}e|%KcnK*nWb2GVw8)kqBj4;BWQPCg;1{4^A31NmHCfu1ZGa!&?i)oxvi*N^UB{6hJ%gu3Gc3b;(x7}S`ZL4c{>u%dERx1-i"
    b"GXarb`c+tHMaA~u&^Aa414QooJm=h*%p_6UzWeUy{lk1RbMHO({Cv)Hp5Nz8?L9jMvmgi}d~{t9b_x8iQuy@07vM8$@-IdSKOOPf"
    b"lwGE~UYl}v^8*`Q>o<JmiyQ9yvg-@?J^0{PRM+S4cWsD1=z8Em*W%?t*O$Mt_WtQ5CB<b%9S7EZKDeVq7BU}sWU-)S?qyjBJn)5P"
    b"ywCh8UO~9aBnlsV^WAxwv{QoBG}2U9EbKQ4g5+muy#&5&_|n8jgZBk|oPscL6@*~+p@4ncc;4(adtrZxD<)wJ-n5y8XE!Vt{>T2H"
    b"p9=~;{`GYA{w*q8Bl}FeLpWA3KaWcg?w!72?S1Nff^f@JW9+xU^`I#)A3&pWI?pE5Jb?8<!wcadJtSXZ`i6}gz5w@ZtT1Llh3jnv"
    b"L+TSg`}^$gv%k;&KKuLZ@3X(p{yzKr?C-O`&;CC9`~US{JvkdY>kNiSR0>Bz+MFG=iv;>b&@|mAR(iTrIYfHsOOTKBrV88_h$W;e"
    b"Vldc@s;9O_(o5~{R0)b+x)&~_A_3pQVBC8;sOWFCC)C<l3mvB}+15fae{{;cHB!_`EPB*N4ko=4YMZ)J)}DwK5eqq}D|4YJRQ57d"
    b"!|!$tRG9iVo@XlS!(!{t)9gkf$;O6N`}WubT`jZaeM)<vG`tAbhr*CxC+Fy|N8rFBQzMmHL!H(TNLni2trGOo^{1fwv|cY&;U>up"
    b"0m({nzpYXrb>eQtwn$L48k@GluB~urE1cR2m$s!$FFgzmK%p(C*kvnRg8C)^Ph@RmEdoh6D1^g7z4QR&(|iHa-Po{Z)gDnGi_1iE"
    b"SD8dAWzFPH?2%YX6DBojHFLAim2)98o1v*NL+8Tr+G8{|R}h*fLl^PkK@U8jF#;d9!NcyCp|9`|rr&}mO!dqY1c2~Tyq`QDvOmdl"
    b"&<!4h1>6OL^gBG$Y)rol_pBwqQNyLV>}9z52`HJW%#`^&E29<@OE5Cx%vS}T`DI9Le#~gXYSi#^UPEc~R^vtYJpSSvm|KO!=5_D|"
    b"u+vNL#i>YpuBg+)?0GFbd%84Voq8=#XoduRQ=R6M_0o05ODS54-7o<{Ov8F_ga+M-)HppVk%M%r#9AZ0bQGlHEC9lYLIfuM7|cu;"
    b"Ujw8HmO<F9yH9wMs+p{i$edH~Hew2g0Rh8`{w9p}4#4O!>MYOOsueL5=Jq7yfw9?#L)~oI)SfVJ3!66D3&m^u^r-B<Kvy(Eue^Qm"
    b"Ja2tEI)WZ+V7>R#JDLPm8@#l>BE)E=LQk$2gq7`ymC>6??b%q5?ml|)+&nMcIG#j%*`xKxwe;czPtV3e>yOW+%&~(y)JxkNaNrI5"
    b"0JWg?ZD*aZ_HfNdgyuH@@@y&1Xir$%zX$Ue4w4EAoqb7wT=DkPS9Lw8L_~!CTUeQ6jUWV@P52U?=6_xQ3J{gq>j-P@ho8q+l>Tuw"
    b"4$KDNDctoK5EdowrFyhap`o?#Vv{qrS8l(c7LrX85*OZ5#0HhokY0KkK?#-YU&Gtk1J_lJFa#NTehwD2)Qk&LFYRSBpcY0<D^gZW"
    b"*Ea?9(zB52PBg$gLvG@$gB&AaT2=$b#G2}aSgS0kVysCP8oELR3Pt9J=pVmg0C!~D!qxEAYFZs-)fVuY*u*&yZlqQwmJVUTYE@kD"
    b"x#(@g)V9SmKRP`G1B?_Xv>Ra(_rgfO2XhO<BnK7xw+(zCmsT_Aq}-wAW4Io?eSU@R<@pdo3jN|hq16o>lzUh6!Y{*>O(Rl>P?(%^"
    b">k(_x@+6QktyN-+q7O;3=5y+$u2V>NY+9>bYZbLtht}#s?1zygO;~~~wYBe4i~M?N*(tsbNXbr^CsHp#`WR9rA=Es3)FQG}Y~L6C"
    b"1Ee~MSB_DeS{<W>>g~5)0en$!tWn3s=nbj}SbMu3wG$JNc%aRxTLvEF)V0K<`6b{Vsj-lzI8rh(MTAHJyaO1o0ZRQ8Hjac&^NHFV"
    b"))SuyU6?>Bu_t3;{${_+CR>6RWQ&v%$<{L2`g5NgYm$UWp_263<#CmQ&iEK7CXjokl1W(06I`(NH`&A4<Qc41q$3u_Wo*PJF*tDu"
    b"&ueu=7tL#RMJpgZ>2o3D0wQ4_=+6j!6EMR!0P^!%?W!3dK9BW3iXD9#?_hQs8~D<n4Rj{%JsS}eatQ!1Lu=`Wxk5&?87e8miJ3Fi"
    b"s5f4F(hsC3<sja(n)f8}_G;c!Ko2zUY2r<5UK;lvP_W#aBzk~AV#^!m?(!sAbGY1l^6$&{kRIZt=B{$@u_Kqty{F8zm>9RuJCZhg"
    b"PnEyvsqbqoBDH<ygXM=jwP#z*KvhWe7^zRk7tAQX;<?;f7#Am$cYD0O@Xp)oJ{l<u1b`s*`vdxV=<T$3k<6`NbPZ5a3UyLjQ-w(Y"
    b"xT!0eDhdQO5Nox8Y=Bs)ULUdQZ_V>L)d~708^=0K$-~yj7)am@d|Ku`f1HY}!DqwO2$Lfrro>uZLUdAWYnfz1AtC~JWy7a}=m>Z!"
    b"K!L%IYgZCt4?6@E$%Cjr1pRhGzX5wpx{XtaF!oZtgZDGj%NZZj%ZLf_2UZ)rwd1_u<U2Bu0D5w+*<}_4x}sm#V@+j3(vo0eh6BqA"
    b"z>&s&r0YPAF(-dVzlA9W=~^hkl4Gr9LUf|_=KxZ`ljZ`DpPHvYovbO_yGYyS`N|rs-%c1<N}qxnKo(dFEi{{QvXe9~(7YX=4TP6C"
    b"dW}{hrsg)ms8&YI197Sgp_HsDLo}y*fhOmWzH>-~#)nbtfY(_jFbBwz60u~eNAAH{!S^_^qo+gANL0!&fcgeT;egV!md_fr{x@M>"
    b"-J4-X<wSuNLLbf)!`F*XK+R`<>4rvkPpAZdeF<oF7f&skEeN~tu8UDcat`Q+I}xv&mb3^IkqQYT5<;H?=1}vMX}+m606mJ=&2LKj"
    b"<`xK4y$wV@%agyWLN*BvyAuXpkX9Q{Z`Xk$9-?1@jA7ait;d>d!b;+EFd;}%biWj9a$uEo$!%EmG-`!mWEQ;x7CkwRAXqkyURVMA"
    b"uX=ub*?gdb5j(xmi~`b1bp%M;AIuR1MDbTnA#-S<TD8rc`2P2wiMO0{Uub%sEVISyX#g;HqX@JV9s#2e?coluGH_ejxCf#cT}--t"
    b"$cmazq7+N-TE_s7yovFrmti2#$jb6G<2?U{P&KE+^rsQH*>;rz&aB)@a_TO{d$azK7%>My+Hxn(>_)fL{d88&7%q(DV<5e;gn02c"
    b"6E9rfYu)~BR3n%ILCl8S5oA(FbV6h*J^#gl;xEA}z~Wl9GvcJjjW@O+>CrdJ`bLR%7xDUmW>-&DCo||HC_o5=p6MH>LMwJsJyjtR"
    b"OpBo?Y;=OKF$Nad*P!|k-SYrI;tNh;r9r+7Nx`Bk3rHQ~i@=@`uxtW>>xGEqDLDmeBszsCqNnsU-i{-R<SC_iJCZ1}r}Qk`ssT?)"
    b"<?pf?7ymAsvF3N#jCaAUdb6iQ!6Y}S5j`b$<Ly*Z1MRH9+iO8V@D#4b+c6+?gs^iW2vph(V6-FQCgu`$6;ujs4QoIuLfnrf%77`Y"
    b"06N3T0&vIp<}#3`?qZCuRV0>_9WZ$mVDcm&7-9MnOxsFEP(>~p-U~~b>w~1#X(0XGS1{|&W<+{`7}vxWkTtSf_q=Uw|E~gEwlC1n"
    b"x%std0nBtALm6k>D<{1&5(_2X{v;3+rFr&f5csFT7yV5oVxtY19PJ9AtjRI}jgPF>*NbuQ$>y@rh_yG~gZb?7+P(Cp1x!8Jt4B}L"
    b"&s891SlbJs{bt)})GhYX|6Yj9S!<D0OT1R{>xbvHNY?H97@?x>6ZD<{q9NS-n<Xg11z&Y7u*rE_(&}n5PJzJ%6hO=C^i2zq8tn@5"
    b"5`BIwg+sp^lV?IQAnyG8vAvb*NI=|whklY{fSD%<t`3+hN?^9rivpl3_yIk`4DGSah^al%2-xlg`c9<OcwkpTvpCS9Vt5l~i0xvp"
    b"`fT~H7;4W2p&K5E1bU|fvdRdJodPGK5BW3QZazCu*ayM`sYwHVFKC;4UG&zrt&)CS^hVMN8Ea~QC_EEZs4tAu1$F#7h;=<fy#c18"
    b"kXlLclhJx$HnhrmV6WIAh;8bq_5`u0Vx%Bd6cJKp7$`JXi8YLbk|_z9F{WgS*)lf^P_E-DeG`BjGm5zxrS=o5g#lAS2JuT6Q_2dX"
    b"iX*1@BZXY!+e^1E81}^r^d+Wh?xj!9$LmS@h@a!=(=(tzIkD`<{(IhziV;()fOm4+l@c~4(DI5A_AGUpVWMbka3@xw0FGjYpq6ig"
    b"3ub3ZgldOJnL%V|$p)tBvwXNXEI_H??Fv#Sle=M=J~kR1`<|XnrJ1*pA}qZNYv&pWm-<n~VTdvN;<1T|8@A|I9xcQsxo!uX1_%Q%"
    b"8$gBa3Sd2~WRP4O2uv~7>J+To=Nn90Sq^V~4hCljP8R5w>+XiMRtGs2CPl!T6jBt1MXUsAtchhtwFKLCw3Rsw7XKm?*}Z_RzP>PB"
    b"7Q!VEyP{jSYp6@odtiN-j{)+mB$a8%Qr^XtoJI8pjy>$>BEmb+ok%gJ{2!<>me$otEGMQ!Gnwx)GXE4aZ^e|zkjyoi%#)4GUti7#"
    b"{LK)<;@Fn7pw2KB`dxs4*RZ*gILh?V6_9-wLNrwh!V0N#(yJGAHq?d7Q8Q=ULe2tP3Wj2dX<^plwRO<K8aasfRnUzfNz;|6?DnoS"
    b"Uu@S~XF&69TZ?p;db0tIWDN(0`);Gt5rud9C{&gDFYK-ku>2>0B@pA0tgyBHo2Y@TPq!4eEwI2Nig2XG1{u}?wcb(3hKcXj7_D^k"
    b"Mh?PqRv?GPXyZZ5d5CU?o;ELr8H9UcfYZrJK*D9C%+ck%%zR$vy}LO~%i$4KWHxb=>T=-2G5sJitr`F#P@Iu~x-y;gC*ba8D8mrC"
    b"6OdnW@6&2Ttwz#nY~-#oS*x+bMbs3yb0meSAj3g@yGCS@{4e9i$YkFiV6yKIFxmG9nC$z136m9vGFdU7$&Luq`|caytQQtD4TTLM"
    b"RR)#F3_48bR7V@~iw{M8T#Pa<_6z`hsQQ)?e1~+?XV67dc)3*~NLKUe<S<eWpB%T3^c>zKmUoh4?I)rRvPs&#NDu{(et^6N!%Q|x"
    b"rj`NkYHi@674ohRk;|ol(CBQ<i=@s$ip+JkpdX%WrUo0-<38azkCZJOWR)CaIVI8sGtMcZoV9JLW;0AC%)$Q6W}H^8!F%=-X|o6{"
    b"qOiFTKnf#r0#%fS1DQWIxl$}K1tthEW;DQ`j0SyER{Z)HHUafEA_Yjj96)ej%Ff)sLFJ3dXulp1*PziAfo#XSPt7l7^E-ygA0%sR"
    b"KweKo<y~eN1B{*Z%PW&o#7Dr(BhfnuLrAh-^t>6JMHotw^%6YXKp0Yz^)fs-(3Dj7cHH+iB7o**YX@taS8^{RBviBZ{hVr=-_NOL"
    b"-TMR8fDBOcc6|NYp&`|v@aTtXP_qH_KLQFtNi#mcO4%R19jak(WO#E6X_3g1x8s}NMj;*0WmJ60dzv|08wliP<F+x0L4!gATNtZy"
    b"W&uQKdTcC^2HzC-zGeXk6JOa$;TURSm9kbhN2{Bs)m3P9Ra)Irt*%z9^J{hWTHQ*mZjDxVU(&J@awdJ^7QBG)2gT}U($`m^2q<d4"
    b"d8jz&&0np=Emfm)abt7_SxhX!4>-Jr6YXq%uC;OGz-b?X9E0jNw7hJ7$H(MHe9BOWVep5^*6~&`oFy0%DQawB)iO!J1)v{6#zjoX"
    b"pX5eZ<pZ@qd3PeG(ypQHcX)w_oqN`lv>?dU5h424Y6d$1+>jo#{+y#Xz+_(VN+!(x+{fqMxiiSDsWamZQ`!^xGiAn^Qj6m?AW1Q0"
    b"k@)7J1xukTj0$}f@La-ynDkX30ukRFmS$66)g^s%SXwtZh?33qT^wmB1<9ykRo4J~ZKPI4C@TIC{q9&KVOy8-nrsUFfFp`g8R(CH"
    b"zmg@u+wnl=UcKHVXudhDMUjD)A+~RhLTm#mx$uddwK2O#FR_5|-|cgu(~8vhl11sH&x?(~bc2Mo3;jl#uU7N<iO&hmx#RWyNpC+J"
    b"lN4x1MGx?jc>7sbq*(WTAtv6l1Pg}&G((U1V7%o0HC+Sv(!2t>^Fey+5@yHG!-v>ekj7<BmE1b8l$QRe6~yL|Ol)>&-hPrsI^&hy"
    b"M@iip^C8b3SZP}yniq0{xZu0bvuD%&T5YdZ-}m;Hdo{0d^P5X2OWMu=^gsAK@`a|DzIIdL?zL>robh^F(#yhP14J4an2irCjAUH{"
    b"ddL!tfsvN}Z7obRj+Vz-y{71R;;Z5_w&gx!#;UMJCV2sw0RSKcYjvnaNuP|iD0ia6=Zd98>(_5UQ&w5~+0RviP!t^lb5gi#TW&Gb"
    b"d(JXdt&EH%EoXyzz}aEz*gt=K)VY11YVS}?@DMgdN5v8av1GyaebH0E?h7X-V#jo}I74x)mEHvtJg92#Su!$6wxnT@M4YS8<9D#`"
    b"S6~qA=83$Z3Gjj1yeNms*^-$$(~Ae!`7wj=&4jLu0r7?{Dxd{P-%JCk_l7b^jlBB@jtuVxRBoN=NgLIT5{h!F8yl}Z9MrsTXx?L5"
    b"?McmhO7ou9yfo=OFcl^`={+pK1pq~A`@?>aMGw$}b5R&Hsbz8Rfq4C4T$Nbw^?Ufr9Ms)9;N_kk^+pYZC$9{Of4tTP>LL*D+pb|~"
    b"1IyOWmYIXS&#AHis`NQ9o|)I23$~8|4kEXcNPfC<;Q;(M4U@Ayv1u$SKwcT%nRB4)L>1`}Vzdp!e?Z}YeCC%-&K`a?oLWN#7C|4G"
    b"q2I%pLKT4s7Zzm1c}C<~@`zmO!C0$oihA2mpd|zyCX>im#7I&%C%z^f41<IN?8F7@y8`e$bqCP0czrqm>VGqHn<0@nNT=Yt>tSJ+"
    b"8e`8Z?SvdU)UB~$!eVkD^Ua0h&dzC-!q;xC6rP@5DcE7@G{J}SE0n+OT8$IL?L6+1;b-XXs<%O&WTg`apeZaL)M>m&mdn)0H6RBL"
    b"<%guwY1Eo|whwxC3_OS85A~C7M2w^b5%c=aqzN&TV+L@yXBnF+2o1-kvhfV)E$^jYu4Ft02yuXf{3slRYT+{vg~u{Rc&*=vp^{wZ"
    b"jhzwHuPn8;-^3p4Nob{Kf9rHoR|VPqO2ibPHguvktb~`K&vug6V|#7od$fj?6$t4TGthlc-AZfwZyAlO;=J#BocA%_U~mi0BAD5f"
    b"w9bpyp4M8IK2^i)Ty<5*D#Csm-2&uJkL^W?I|*5=-|nKFFqZ8n)a!|FDXFu^>w61VLRSNdpZ?IsjJlqr^)b{FQ(uHE@IIih918K-"
    b"6?)#vOl_W|=BrX4A$3b5BV(Og{q(ymUBdKwt#xJVWHuV;DpFjnwYH@YI-4p@`uv!ll1Zp4K)Y8N9Q_j^`^_I*MYXw?7F8N*Au=^c"
    b"U{vr!Ae*~7vMUVJ>2K~pgSk7g%HV!GchZsQ02l{fe12c-S-wa(^PPp6=jOw+Dh2wrAnQ+8_Wd2g0Ds(ec7}*1%`j@Os~4hzF1as|"
    b">Y1Ky5VP1q)i%xqn!4W4YGKJe^j{{L1a5?$$%O@`-$U`{9ca4z!hLAMpO?vRR5Oow9iDEjdY-}dL{fb#ye}D$inNWlLQ{o#P5o{R"
    b"H)n^m>Rah$<{H7)Kwn4nt?irlP&!)Dyp@|+=!=+G-`Bhao&)rGM9MVI;8m@~5xo_%llpY*tW5Sc-;0LU7fKfi8m!=cO+i7N7O!Ep"
    b")H6}U^Xi$v6SS5$lHQXRMhN{#1%YuVy{8dZZ@@i4K+mn;cmrS8+qHTL*XvxeB#opHLxW=bfa`qt?-!4hUy46|_=>K>+PFwAM^<;9"
    b"DLDUq(i3~feEyku9N+lqY77bJh3<lkJ31aR!JGu>?_j#REkbHsyd85vnnGX4H1;TD%Dzy*%YtfReQY*%-%I1c{^rDOl|q1Lg2nI;"
    b"qj)YG<{HIvohH!hT3cmokL>A0rdKanADg2?Pg@-A7h0@g`ll5P&``G@)N_Q&DSw3V1%QVmOnT|-D>%cw&~g(1KR{!DV=|_RPOadU"
    b"5m$u~U4r!1j<lD}kwS|Y$R({B_;qv=7WvZxUgY-+@)iM<QsT?{=_Y}7hXh4`fQ}f66D2|g3auUJCpAG2psQR8$cWI@OhCXU{?2Hk"
    b"W5K|h!d}%o0@SjC8^ZRA%9&XJhn@NI?gE2;_A!YUWhieSESexu(t(Hx#<LPhB(!V`(ure`+Et+7sdBTVgQU^m`qf*Y{rbJ(0NphW"
    b"dFm!R*;El`<`pNrhnZ^o9Lo_5&>PEHyu@Ct{4$hN=rbz}&p;2oxttHE(}M$H!^ore0B301(Kc65$HFYbT>F&(4VoEET+_wW1yB`G"
    b"i@;e}(=}9|mqTH)ao&q<Ovofx&p#ic=MmXJlY=S#22#=Hf56>me){SfoQ*l?Lj$I0^EV@92RS}qXFy)lHAEkaot=TSr;nbRhgLeN"
    b"?G8b8GJ=n5JhD2>oE&~yRmB!&%1TO&mjU|P0ya?w9__v-yLh5EG(VeJ-Sl>*;YiHiIv)_KkeMZrhKA_G5Th2XJ%+D`{h@#oZtlTA"
    b"zv+U3PL5>Z8$dWQ(NCY<oJH+gs16m-EInrMwu4II3@Nm63uZ*sSYmB9tmz7q78?LmihLm)r2ovAAE+JO)n5>rNXQajwl-n`l)fMd"
    b"f^~OYF+#C=UBm)#eUByiWK0UG5lcX!hariC?3l7_Yh)ypdj(VKFm5Ow+kt}cNGSOnCYJUi$YS4Sa}0u*Q?rp0Vay^lKQxg|mTkWk"
    b"dIe$IRoo<}E`%!(QT0~1!knwlaPzS&Fh2;hD!OAR=FLc5lew|+n>nc>e&c@e8ip?Mm;Mn~+_%sbe*XF0hY`;EbWRT=7ETKdO6X27"
    b"TKJ-b1zs8f1-fHJ@I9kDhQW|C&OdLwx|!7#Crjb#S7@?`J8i$^hi3pyM4&${V!|D!l3ethwu*y1(H%R_bf$gQSL_b+{>lo()2$y8"
    b"uakjWEi&@0YHY~GS*CB!L0o{DlwNFsD$ajDCrd`(L=OX5KM$Gqh}+pp!Sy$Rw7|0H4M$ch22!tEm_h1#d=sEo*dhQH)7z|$L8RvJ"
    b"me5uij$YqfGbS?;_l5YVp^5I>a|DRyGR(3Qvn+%x*;Na9&p(fPIVv6p{IKYQ0kjY-#n1}ikdAh}Wd=&B%~H0FkLp<)LE0BExNa|9"
    b"iQ`EcjS=rD6n<M!ky$>I{u<<WvSd!Ywx2J2Vq;7HLbYs*-Wp`~u81i_f57~ep#8RvA<O5)Tl&Ka8683s6V!y6)z^b`+dz}Qy=}1E"
    b"lldb{XSVNC3(u&))ta}ALHt~ik#+DdwysPR&vbvF>)d|IpDzr09+%2}o^s|pALKuG4|@LX!1I|YXO8_o^K{?<>2&W)R*IC#<4@vu"
    b"rMLqwOnI;|6TZxJ2}jq**_W2y`3d$VW?ph8Em(DXBI#q54;YP{+-PLWH5xHH1leRqt67Mqma^J2Cc=!pjrinT;}cWE08uob%<Vp;"
    b"){e$PUw^!{-yaC;%3QKZ4o3<Zzmm~9XA?5~A{1tZ(%cG{7!}%)0fqbHoBILt^uSzTEey?r)LhSHfF&pcOb#~h%;Mm~On8+Is=W$Z"
    b"BI6=L2yK7-aj5+;0|H|>w(M|hdBXu(8$!?HKqa44zFx*+7A*w&oNY+SLHb~a;@Safsp8Op;aAF9m5dspG>knI*#Us8+L_a0HJ?Z{"
    b"5NXxUtgsx#c+gR>lrtjb(rDo;PXeTJleWEsLTTI9QTl3iMXa;HPk)YvmcvFKG!h5xoc<0+eRpHfWtKw2`$z2L2zw^`m-DRqQ#V)n"
    b">3x4zt*lNmmb|J57B?oV86Ge}fLjq6z90g+^`8_nB#cg*+u%}f;xhp1lmm1pl$uhb(BlHI=aW`R((StX+BO|sH&OJ;umW7fvZEd*"
    b"1?a*$zLYj$XiE|Iy4x7-$}BBDU)<HchC9!8nE=r;Q)Sqbv-8IBJ2EwPNT>HM&b2WeotN1K0MbVew#u2Ho;7m&33W0MI5G<Q;kT1<"
    b"!7zqo2b>ChoMFF>q<J6h(5H~$?1FqDl12+*(x@*Ne}=JdZ#&B<uU8I+3>NZ3jCAPzi4E4*_69jR7uRQq(dT$vz?fo_pN_51kmRvp"
    b"CH^>14$uV*f;K3ozSbC`zrTwO86+Nq6mxqs%pj}{DIDKALnld3_l7YYN7~*kYTGkohpqFHxyIAI@eiJhq<dpY+uRvZsatSWdXgK?"
    b"=d;$F^#k?UppzhWD)b*f{ziF2T<GdvywD^J;m4TKop2v**IREuRO*mtwOyLAVQkx_+c%Gb#Q+G`dCD9+Gh<}uBF|e}Pc<~I=^8A5"
    b"qAYjc=TO*_K|aRFFOa6z^Cif5EGU~ZXXAT2u$vKa)NtOJ$%MnW_b|!}4>C~?J;PS4Z1xOfx=bz{&_yRJ895XbrZF>^sd^AcWAkSh"
    b"jrj|s&~Pn^i>sAjy!|X_aLv!KDSgJv<%X&75*8r2GN59f&8nDrOYjO?r;*i+M#Q(5U^a!WE+5c0m!kpJBG4V95Haw*A5!Q(e1z-Y"
    b"j%K?QWW2wh-K+ChiPdxyWbs8-hiJ(_b<zI-S`WaId5;2g%FH|~$5~oAYA9D{^Pw<f#0zenepJE&G(aj3Q9sO22t!lmj^ZII0`Jf|"
    b"y#MJq1ldpHwI>xil}+SHQiZPl_!blW`mI0@7ozx8e=-zV9l&ru9ys;;*&K{A#u4MZ$upQb096L);S#P`HBaZEG51dA8sl83u31E("
    b"vXDnj(a<b3BY9;7yRs6xg^?c=Ci$1}B6hXFy4{M3_8Oo)q{VI+4WyKru?kB3&{0}`7`g>g{he+o@&`e^qt4p?6xTn3%*^T6-$KyJ"
    b"sJFkv_)%Xt*!-h0h*`ga<(gIM_o9vKfyip?`;XjgLayr3v7jdf6;_k}7KW+xrm7hF?q%)wmA`o>w0;0OOoSi|<Yb5eWFl5z3$P-P"
    b"2xD4#D~}lR!?pdw)|L67ST>WzX}mzM8#4fg|C-4mIq6moj&`%o%owzU)peK_-pZ%+Ryhwx`smqdMttlvp7G=~o>7zsYzc$b4~ieQ"
    b"c0D@Ma6b?AJ}=DmKF`ecK9}WspT{%rbAQ~|&%DpKW5>AHcs+WJp%yjkHJ(XIwq(7=P|Mb=*LXa0KKIAh_lNRoL8S%oe;{-sBi{il"
    b"jQhlhUE3mRTXG!3xJ$v2v`qZ~MN0v`>Dv|DN|scuz<@e$L))nXq0$A7u-k@V=xd(5DdXtqo7_bM_k(3lwjO1)cWBZ6ctd~E%-XkL"
    b"`=kzu;TMwLJ{(EXn`Sagm8jLGL2U8%sh+6lzK|M8YSRie<JO`XKxJ&?ARPx}B1G@yt-@;-YTL>5q&`^D2T8P_S8gGrBPM;!#S;@x"
    b"T>qN}(zVKPe`F_}^$+ARsfkpf+ATL}1x8Pj7S^Aoj*O2Hd)ALVORKj=MHanM3xj_E+Z8}YBcsec+NgMK8g!$6I*WA&MiM=aM0!9T"
    b"0Q|ZXvC+>j$XeUjn6A4S&B9E+VOs%V)(<Ll+BC*gLRy_nmOE(eZKxmFE43wd!~!EC?Otw9I!qsQFcNo|K7I}EY&s0(@uv1kSVI8^"
    b"y9@d0jtR_860d(U91)R8|IUFXp}+MpRvk-=YGJ(gnbfu65LAICqa=I(5P$FKhL@^?e#q*3gMI+lSdY%^AsA8q-$wdT2VY@B>`4G`"
    b"1T+)!Eo8YJ1bM{;gUf(@D70?}XzK>FugrmWb4d{yr-0~FM#2Dgkmo>DuI-O|0a1Q2Cj<9GhGivJYKHdxETjy%etf+hu2#TIw5eO%"
    b"C)yL66quUi{QRl;`c3&$Gd>j715-&+yiUg8oiae55V_Mqf6O?1e>LeMqZyI*?Ah=F84sBkpu45<hAX@EM;i)Jv|DBLD+7;n=tO8f"
    b"fC}gXccQvA2pp)v`$Xs|hsfL<{5vz7;a?3}%L2_WU==ss$vVOU(E%hsoSgy5!NKx^K`-iLwu4Ec-@6gL5)Q4^skN3ReXeUj%1c@n"
    b";A%y>Fr2=5-1Eu$CNEA4kigf;^d11_09j#{P`(Rk4T$eNayAGse;sk4&P75pZbiCQI8`OYTcxl+B7ijiI%K~#`!<uvKn^^&sEx<2"
    b"Z?z?TY?B3$`7Rb3)|d%%$ioK)ee6Mfwg=0g2Y#jsyW)UXAqkeW9DsR7q1q?=Nu3ygTfbf^vJjK#D5EI@-?+KXxW|?=c*xpfTXK1F"
    b"7Y3Z^r4p~DQ1g{Fbn(JnIr0op46+1E$$S`mO@)HE7jr&y0=+<IAq!suqRug(#{%=h;6_sV0ow6o%=x6Thja&H_P~0h_*Bdo?+bps"
    b"pJZZUSvl7CF7sDFYJhHL-1ZoK8!Pa>z?wKOFyZO{V){*J>R&FAIWlh1^|PIv<4ITw2J|;c@3!CKylgvYOw0wW{QZx3jlX6abyhVr"
    b"W~c<p?^R_O*1#R5uvWDy*DeGt%P{PF@e|*-&0QTeRVuMgnf?Z_dmu0V#jE5zj9`VMW_O}1S><5i5}3U!U%s}n-JOWH*pj-djRCe_"
    b"!wq9VgnHwT_hOvAKLFY%EWijz!|QbxcrW<@QA=%nwmldKTqiB@!-7L%c!*9yKtGOo$)Nz9fmff498&1}P~R?&${bP|(l&U(LAN5s"
    b"@j5B#V~3Z~b+d5Qx#-^OkfBwwb==VPiSbDz=6>3G#%kz>0$y{+^>~%&hqG{9|G$gR;vtkQFw2%7mzA&IHC0%I4aN+!RZqnBQ%tXs"
    b"b0;?|e;Do-`pOi}`MiCxZV6V^LAuV((0B~KO<c!?M-Eqf`wbLcXW+YMt{aY<W&JtiI9gzA+L}Hj^q|56mF@?H=n)A8|0Pqn5PAn*"
    b"y%d#<czr*h$07PXH*>RrVgZDQEJ~Yu;_9dZ%slHlt~K0(Eu+6T`cn|jw^JCPFGR~`bGM|}u4^sn=%|dnfcFo&!uoN7^~1XTUj*)t"
    b"N=O>+gFZ}u=Hfm2H-3%RANDg@z8^&R5$<eSbLCjvK)V-GV`YZ5_#|knH)bC8Qi33jo-|(}b?GW{#4zx1mC=iXimx7N!f|}w0Kz>}"
    b"xFjB!!p22f(9zlcMZooNx9Ab{dMQl5Hiw~L)~z-GaZ=?9#UFBop<=fVg!&qVUi!SrFryUiMkv6%{no`z%w34D@j8+IYBF+g8#JOP"
    b"ElSQRVD#9=(@^;y1$bM7hZOM4SoS$r4#UdIvw*|x7sw@8F!ALgZO2JkBE}oV*p_rbbPU_BEVKQ`<W+h*fGgL+W<KZ-(Z8DriDNZ%"
    b"fl0ByNt;_MvRMGbS+4kcljmIY1|(oEzzy6%qWGb{<PE4UzDoaj3RjDYT*G+oa^p3OjaO(<eK6K7HZLB_qTTcxcr5xou>_#pX{h@k"
    b"{n8ESG)yBZpw)tSPsi(f{q73^MT_=o(LNACv}jr{y_@g!9X~JHufpm%O}{$XAeIeW_c~42PtMvf2F3fK_;snd26|zLH}vkTE$qhl"
    b"W>JBT%tHJqB8S)s7U~Gdh?S>`;8oFNV@X)slbqAFpHMeKxdBxYa+!cI;RynjxGNMlf3Amw$ZEKGtBj31Is)!rngo?P<F&nP^j|JR"
    b"$R4C#wk~?<zrkBF9y$>i(uuE5%B)M@;FiCB9d6k#RWc1<yzXO%vLI87TEh)|Rc#(YU4Xc>Sp+0E_xKh1MGWs6g(9FoZ9WpOF@cU)"
    b"2w0&S7<Q2U-zm5k;vjvEFDe5WGV+F~(9`#t1TqfEI>x*XZ~(^7Dosq@=AzG++U8DIn_`#D(HRVjZ)w|7usVv{-sa-o{<K-GL>0jk"
    b"OBblO#nP7Od^YQB(&Gu-90XYxoT@T5jqv3}9>+JacWrH#ZP5|g0`A0MhYWNBSJ2k$S=-lUTP=)QI45@RgNCi&?j)U1y31I<!>n93"
    b">Ph!9(txzEp|UGG-n(!M9+K?%Bj|+<zk&yn(9Vf$mJFDm9}iE~VPIauPZfY=cP~<zdWkub@5cM;{Ek%fjsRV4|0$CPvT)I=ZPx7{"
    b"ArQvLe|ZWaV=VkdX*90gWik=3jcX7+)>tQIyv(wYdimom?<@}|F#G)hI&(btIrJK3VJzHs=QEl2dpb81wk=$(&dHeTGxk5M7>E+N"
    b"3?s|*Dr>ig>UgwCZm07~4N$P<q$kgQ7)KbmkG8#IYrAB#etQr3Fm|;-y$*equZHP%CV56#fPvW`Ca>bYu3pFy{SAWphKV_$AF?pW"
    b"-np2~=NgF}Z2+pj&$b(96aa1Aei>!6_{#=f&Sq50x*daW;=iPsL6DG`4}3Wb{O1OMZw&PaK>kV|pSzNU`>XySeX*4JHLm0XeUZuh"
    b"Dg*lb)#@!nfPN8by)wv2VnCV>g7n8`MWaVM4%EG`%(lRWYvfW)FHk2VVJH&}_<Ci~oP$UOrh)vR7ewF5_+puw%=sJFkRz)VdbU*H"
    b"Aqdv(-^HV7nI*f384&uo=P21>>zLHBfBx&yN!$0S<1q5K!Ni_f>~A;5{+`T@{jGaN8T;3i8;6MCyvE=%S$>D9mTPiiaE7x#apY(}"
    b"5iK@c4=CU<`z9`uD+8=KcFDA9blW39dq%QNW<P?VrhLFN;UPq)<G?K$5^;DeJlzJQ0jWeNZGO|Uf5RXWQQ-v4WcGX~4=QWJkV5wb"
    b"x_6-wAtWjEiTaEHQ%oO2fBxJOweS^_5odIZBM0?|%H!eqLwU?+H#=3J(1{kC<*SVN5%g~{PV{AGMlc$nw+c<J&XUQ>u8;9Awx6(W"
    b"{|2rF^dVZe$KW=^#4URKZdMu@YM36VVEvEQvXO@9NoHb{Li8sCxr*rzcrLXv6r{xqg@I18Qx8J?{oahnN&-!nzE_cxE&HOefeF5="
    b"vNj&{pKDTPx0}p-=Ju{Z{%@3n3h93!yx8t9n?mj7MvS~P-~or^k8UxNxd+#0=gGg#B-@!gvTIm;1CWt((ecgSf-KE@0p*)thA(<g"
    b"1wVX-^<r}KvrH5Nb&bti1$y3mVs=3y0*okS5gkqKx_VQXs;>Y`>7jie>TFGf=@)pydyv5PH(nlZpj_uQ48?%zZD&+ZvoPF<TAO#W"
    b"Hnmofz6L3=g@QVb+4WgJSO{&aO#jowd<Q5MjW1xxOAZF;R^CCFhG6qnE=BG`$e=TI9DVDTtXCyr`r0p9uYL`^dg|EnMJOsxWLwCg"
    b"z!Mls6Kr0K(AauAgND&A*~FrvZZFM2`FxjmX8xk%n(s#O(SRGneV^FSMJzDhHW+XIfDG#${WZ=7e?zM>Wd_@WNR`a?_iDBMQ73Pv"
    b"N@OC!KM4cw1yr-5%y)K`(~c@X{l<;BId{ON%}I8UG3zUN+_0seSV10GjIvR0`-SLD&2Jzy4<(oImS*G0>9lpK;V#WK8KjY^hI&3M"
    b"Nyu5R<eVDJ;`i*SdH6j*@%;4o4al#M03Fprk~%r(<#4|E9Ow6N?HLPa?@f6NC%3%^a@({0<?RiPpJ!1a^>RdrSU_Px8w<5Fo2g@1"
    b"|8Tv{2$|pwcNf4!+JT)~E*^<>PWJR{8p%!n*m4)~I!UcV@dumfSoD;Ai2>5CS=ifw{b+yve#-v^e^Z;`Z`z*gZ`zUTZ+h&n^fxj4"
    b"t@}j0RZLncQ&mE|&aO3zTBDRKVt%JbW%}X>Sbs&16uNy5gPN^1lxYo9wT5Y013NBjRoBq?m&|?#`^W8faOLc0Am`})`Ti*14WHnT"
    b"V*3r5m5)?8hTpGBYRcFFC6&|IGS9Y#{FYpbZ|>(K;iHN@T4svc$PyRdk+8pvx4qm(--gA;PG`B;$Ttfz`xx|>M?GQGH1l292YQ*Y"
    b"kGb_&>r|}PSLR7#wHu9U0luwMwbnANbsGKS2qe|6TuWJ|JZoVwN#jm#zULW@)MQ*p4=gTEa^DdzCk<zxi+kmWiPX6iKQu@;OUx2p"
    b"srk4iHm8)aSzMuABbcY11>CWXIw4o2z#qWkb9r%)>ac=>yb3<CyvWO^i;VIjmKTSXw_%*eB36M+TCfhyYm3(v_~Xm%G*ZO&SizgH"
    b"qY3hw-)zzf8Z+IHhqEuDeL|r#NAO6>HCQ3(jV~Ad@nv>8!KhCnL5DVbzWFVXL9kD&GW&Ic%)13Nz3`Qj%d??XPz{inY8S|uTCI#)"
    b"2CMC?h1WI{Y9q^B0E-=BG2TDoB0ce~^G&%XwaW9)n5tcd=z}C;nX9tV+|!^fb7dqT<E+J6#=-XO!VW~u2u_Tpz&jfYLBTsa3@)c@"
    b"EjH*{CQ_@#uGRPA^EpGcA(yo%UApae%#_az`daO29x0}^oQ;bMwc50~6FP+UA#Y#&Zpj403s9Ml&)Uvp$7&p7M}6N8J3!C1s43Rc"
    b"D`-I%*#mkYOwb{~*J_73O*-><CFnIhre!Y3O$BudLI&V-kVI|f%Ngi+`wb-s-~;(i59F&&192b7xS#CF<OAUbKpC$xAs5Yw-{bM>"
    b"peq!<#O9B43BXOxB9@X%7-Hpw)e#Qj@&M@4`a*`HK)1|EK+?E4-<YM$VG0-`*@C=rR9Hc$Qk`9)E?$V0AW2ST|9AMoPJ<tOJC`3k"
    b"k;@Oh_gC@*qyG{pTY6N=<Yf_THombK9k&>ZQ0LGC4)?xBPfx?d#KmI+@q7dHt0sqj*|PMj=2Pew>#ws)t8p5x9!VG`zSB<XoK3_o"
    b"1?bI%%*76iyh#I^=VYY8+@sYw8-@m4=9Oo~=Vy!a(qdj|Lq2jJ4UuXmS!NG+*i8t84=Y1jRMM)Q^d8(#^N1Y~dZUvZF<&HU15+b9"
    b"M}N%SEzS_=3z)Oo*=X*Da&e!jVb!qx^ABmTl6(jypgkz0Xx@JM+lkyXbP#)8KsMURBTj62(84QjZ0Ht&(kyeDdtixa%bY_b@=SZ7"
    b"cx^v1hy6jrpo=d3`hMv9ws(zar2t)D!o1SFIZiwHfFpXI9iz6NzhrIK%5+x=_Y^F10>@;A8FNn~bf&?)=P&FJbc6S2QGmWX!3fDU"
    b"TKi;BKy71qK7>iJ(I2BT&=(LY%$>vND@@*$7)v1=>|ydZPSQh;Ljx@`um4qE|D8@o$nSKn8e-o<dBrPxsvMimT9tE96!5_QQN?LK"
    b"LTVhIBbwseWCra2xOibE|2Sf4apQ=rFO>M5u|&UT4_}EnA`$6KvU9AHm0XXil<=tO0g3I*mrQ~%bp4GUrm8{oAxsZrWG3)F3wQpZ"
    b"!)*-{y9enPESeLYEt_VdQ+x3wU7<fU%1$PaipUFOz@$8*T;?E+oLJ%f_>cAkIUXHLpBDxjl+d$sKRc2emni*(gX0D>^^X|P{eqys"
    b"sME+u&$*2S&;vji@?jpzEEE0omlK#&1K5I9xEr-<v4ORgQQero8m$^d$tng~vJ^J};<3Y()*p8c0bn*(0Yt)kCm1@GI1sKhIADwK"
    b"PY9jQ->+bKM-XzKZ_GYJf122a<&Fb8yd!ti7Q<6<zW=5P5U9zW=;&;+{?}`rrvUHs-{buEki(s496JEhdOAO_b)J!S)Q^D5ph|c<"
    b"DE^k=?+8*~d;<@)m3Yi8EL5bVouqaoHnJxZiJRZvQ&UUPxX@A(xkWD(f%QF&30;HfHA-X1ExPEdI+`e=7NnnRx<Y!X0EIl=QB!4u"
    b"5sw^VCaz5W?`HGs4X6!DAw@6ke}|W;X&7cd8gEba(0h5&l8#Xw_454v)^B5lA^HFdNX9uVD(^-d9^Emn!z<4}9F+{|x{EbEfd6zH"
    b"uc_4f3QBUg+3uNf%pArvRMy<Ajx{pIsNNEyQnrB+<Z$_$vCF2YICqj-3>e=VJ;91}<M+qxr=!naWvz`JXw7n+v9&LZgLCWH(9J<;"
    b"F+{(6bx32Dxs##=<Z6dRdeMfviX;a@rg{83_3|c4Nv4IxGgu2;<<6B$JIqWh-Ja0uCH2mf8L24<<@?EbcjEjHq7&k?Cy*}BZ#I@F"
    b")W*Bw>E3YO)2)sVQXQj9jzLnJM~HUwb9TDeX-aFljNODxUUp%8O_6c7CnpBRBKI=O_p<^EtLvk!XfnDzH(<4o{sXK#rFmK@T5t5w"
    b"RCZ<?>80i(7OJW?VJvQWUDO?~Jw+dUhxvp2c>ka8V1zv0ZDHXxr|5b}!4t9i$an=^j`qP#ea^y;3e!W=GOhfhg|!m>2YihI`3>A#"
    b"IXe?jvuknQau~YbyBGI!{~-I^oLFBe(C?IH_j~jASt5_h_Os~K5;RLgcD+d377FY3?@;a8L%JRv5uyoROP&hOJkha4-?q7|fJ@01"
    b"7zOE6R%iz=1<YWlj)(OQi9f;9WIz*?D2tQn9%8>^kvT1R=0csQ)k&miUQORtyN0bAK`HEq0&sc{(rH*n5k^|>DG;(RhVCag7e>dU"
    b"jietPu?tOFo<wVLg&^U%1aVnFg(_ZSLtE)Yb_#2^SR{~9+QaE#>f_45B_J^)>AwNW@+@&5U~t_SJfH&+uzT?gnX#Sq@Gr#@vR2eM"
    b"Ts+R1=db2&FWyN^42btbYFAdDISx7>Qnk1^lS$FF5}geh_~s{sRr@|bt7s7&1<*(p(l7$WOzz-HR&Ty2l)q;xv;T%1cOMOVKGcGu"
    b"7L-`HX5Ka<a>;W!Y6HglGA_w3!=@L81f(CJ_<6F8kgi;_AKF`DcL>o!`c*7>d#tt3)OsU1M1O*hzBC3$A-y7XX>!M)_>+Nn#c*sP"
    b"R&fWGv7m)uOP}e{LeG}|Rx3<dGal3m*L$;*k#A4s6LvgAe~fVPaB(AFJRI5BpjD;G*j3%4El=afYkzk?Zi$!3C{pC<QST)FzF22p"
    b"`_UH3Q&I`bG+IPz`r7xk*cDQl#wdhG8G>hVHG##8w4CKrGzg(H@@A<0C^;7$<K7oQl$^`g35WQAE3<Jadplv^ZI1l|hHUO8$APTh"
    b"9#-gu{(*t#hxpXmAU$d)|4lm0SB60oBmRn=*NByH6;L1}6r!X_RXX5jPK$Qz1n$#d{)XH8`Eih+<HvaC#t7upcMkWd)Z5yR0=n%>"
    b"jmjO`(neq`Fgl=?HEFgDq0DHYzApd`ym^H;aIk-H1KIfodGomXV9bN_R&<4}hnl|lmcG~})1wQa?{RsYr>6f=Hv>w1LBSxnm{H1B"
    b"(q@px(_|tErn|)nLdJ4~(t6q-QUZYg<SHWHtMn(A5&2dPuRr9^=Za69&-sJr)6YU3_(&=)=Zyq9skQXON~q~?tsv{uo`WFqwtzT`"
    b"QAU0QQk^NjSsqxO^(fkbFw2o%(fn!1n7)LS4)38f?6Y$a(6v(Rk{&GylZ7MqW#`GF)uhQdrc<rqM<jE4tB_HCb}lG)`bn`Kov(vY"
    b"4dtDK&gYVGgg~l5;X~P=5+-M%r>9jUz2z4@=~fnV+DAK~n-L)lC=f!xzk8Wugtrfu+TKeXBVNADms}>$AQL}`@#-KWK;53+)&kOt"
    b"dDr8(tr7f%2?BsPRQ_fl1pMoAE-J4x>RoHpJB+^ivGv<nha<@PLw+E6GcM=i@ED`!;=G#k;Wz!yfnQGkhCe4iJ1>oG5j;r$5mzYg"
    b"Jh!3K<<K<acQqn9H6w#z@)d}Yl0vV)m9h1~@+Oa*bi4Hq%l3piS7GuwmnR(^79~WV?=!ljO6_{oLayQ|Tp?Q4$2TmAST5SruB*k}"
    b"z;eyyX>Ch7$ERS_4^`2JvNhk*G0GpJ{%p+?LiCOEnfk^B=#os%=$o)uwxr9in$z*+CRnkwANOO7#Ul{@hBbr8y#nz7{f_B(ss<}y"
    b"%paZajZO+XQdL6N$Hw1k@~7?JmXa2%0(w3-Ugz+1sxwJRKRQ|WspCn=4iwSG53RCiJ=6-FCFgnobM|j%ZHsv1>;C9XL=njxv@d$z"
    b"j7}hmMCMTbP(l=$%sI;*)ajlQ<-IB)>cQ+Kcf+mcNOU@>kx1zZeAtiY#>!8v#{0t{=x0xUt+jywH?zU;jdAl~lKtRu#{T(<@xddE"
    b"_+Z5~Y=Cgqe*`_zijh6>-+;=P0J8qd*dwB;RnF`RV7;l9;*U5yNi<t()sj|igA|}D0Os2~8*Q6%fgH>Oay0{T3RLpfiaC(0xtp~b"
    b"mr{A`s%>+j_K1|4^i)50g^wVpM*8IxO!qw!w=Y188*Stf#B!_lh%Ixr9P1fpyudv3#2c+z9%SA4gz-ttIZ|!&^jg36H1_Qg3HqhA"
    b"NSh1e)sED};kvfF$Oy`W&S9sdflf(yTJkEgOlI*&8IvW{WQYY42sraHb>76`<>JR5*`Xr_$Y8|UM%g$3RTBI(K7!+ZROYV?^Nl17"
    b"_W#L)&Nq{c=fUeODZDVS*oI$k*NphI^(H1QFR=9%9iNRSkobkUw^=0Thb%xu=7$L@TAfT2%<m<0N|NF$j`(e)N(5kxhP0X7^m7Z3"
    b"Y{cKqAxqJVd<|;R#qOh?PK=Y=)5Y!{XLpI=><#Bgok%Qrpc1SLC+;KRq`O|yVENXGcr>(D1v(Sg#n|t47-|_W4<+j)<1iv;rWiY~"
    b"S2ICwqm-Dr9lC!e%+@xHpp3MNfEm}~c8HdK<be1C>113OBhFl;r617yJp*i6Ac{g}XG51^pEMC02CI+$nDq_s^5@?#diI1sezs|T"
    b"5oQC(%nWUor%D3FL=iQ=l#+;zfGV{?#65&jGu*@C#U2fs^*sH|ihg|h_l8;^VYCPtA7Z*Wy4V28GQb5Wi9C<CM9kg~U!OKmp9M7i"
    b"P;PajGE-&A)Fx$a^Uq_776KZj3J5MQROsf_NUDTS(LW77Zy*~oBS&O<mL1z9rV5D!C~BaJB(MX#WIVx4LK83Bdu6NA>TH8uARON8"
    b"$O6Bt*|aKIUuw&@*JeVnj1>r-OIC__I27={;pUTX0kc4zR)s!R$O)*$IB^4GyA$fv_yRlxNC?wuW)@s|NE=5klOyf~5}xOQAnp~B"
    b"@cgURAm$6vL4dsb#JtIB#k@vwQ+WtPtl3Wh8ySaNR(AKIglnfihby@aCg=mQM6C84+i=`{qJdaJ{uDWFo=le8v_?s5lqtbOXd7*f"
    b"hJ<nEyLrcZ4a6tSB0hV>6|b`?etHuMOLchA5@-qU7A|ey7hha(cB{3Dgb;>6BB*O=^h4ZzCdCz;7+8H(XuBvu^9%5?l0LXLXm<ju"
    b"O=HTPQoP3QKB|odd<XRI8s<EZOYRFDBT3ixed@L3O$C~@zOv8!ruhi@kpAuiUGG4z_V#_z_ei(<=*7(<o^E0zMF4C+S+En9@SV7$"
    b">wJf)<M4b-)VckrYVWAR2Ol2l+Q|Ymk48^{=2bXxU+g&U#juh)V0HIo$$3tcUY3ey?cElRrtGu?NeR$uZsHUT1u2%WD{OuS`S3F1"
    b"i?g5TxD=!#b-tM`x&X}tC1kl6F`=;hG)kt2=sL6w0CM*RVZybLNKf=KgAdRc`wl=Nywhgyi2LmMaYjSo>Bdd)*N}%rJSk$64M-GH"
    b"5@}H^A$s20@F5uoM12xch=;{WPjcf}G9oT-BcmZzs*H7to+RXfB{nvW2aCM_N7RRGv2J^a9{;1E`N=}=c^K9ocgGSyF6Og6{F1g_"
    b"G*%|^s?mTpXusYGU>_SIGyODJV3^IIQ-92f?_69a;uc=@MrL1SKj4I5hIuQCr6+8%><T0A5i8?&m5DpxW%uH;!ujxJSq)!Bc-*|C"
    b"#1%0RS71)000y!1tshZ~euKz<1TdE+#TV(Tx~7u^|0fA|q62COl4G5xB>W|Ui+k{3b9HP-@uIoM)gyqNex4Nl{m5fs($)E%Ej02N"
    b"Dc-GLz1oVwVD4AVz2-}?b9$^-cOP<h$M%TZ-VscuZBge9cu`-+izzB?!*fB~qI(+}S3#G^qW-zZ)Z0L(_~YD@>P_2EtH0}{Hb^Rk"
    b"q?3?jfuuK5-)U%MJ&rHB3gzJP5x?}~1^po*I^iZkcxvhc)q+CxsW25KWpGbQF@>B1h?jpD>lQuT8*2jeZT24DAU#Up(s$mJ30oaO"
    b"Pu<A&!*r2SR>d65SpMeIc<H=c5SMpqyl%Bj(q=w|w}4wu<CT8@MuBfx!ueBZ6IW0$VE5v&nq2s^UmK%MJXnZT4NY4k4m!5T7zR>T"
    b"=F($Ntoob^BG=F}mYf5yczc_sW|HvN7^GBWV1@y0!WTQ)q*^;nRRCQNe~g|ZreEMJnh)dD?SVD$9Gfsos`??@^)LYwo)ZLJP)A{q"
    b"y{;CdUW-4hr%K`vUrkBzhd)Z0;}7@a?^PJ}U(+$V3h2<<9pjf6P5dEMsEv;$Mb-{687+~~*|y$+{Ij=TP;a`phqW{YudJ!0HXd=i"
    b"v8##SbT26ovJZ`2JB%xi&uHGxhgX>yULj*qpE$-@Fvc=I#<2rqtkSX8^3JY!)z$3XN7=i6<Bt31&bpu@Wso#ggATz*h%YXi7E<D{"
    b"nEZj{;xgwVl%W=v*#RdWrRxv{d!Yz&n;I;#Wfaa~H^ZOUURM_`bPyHk7>=1nYVLVB{4^dLS}Hrq5p%ca>L$sPwtjUBkm8H%hY6x~"
    b";JdMR&9O_;hMUiSUoU$+tyKcO{{_B`oe?+4u~TMqk6zYpgLJ(tE_GB2JK_2mJnnSC*In>g51;FgbXay2b@)s>mY6zx1yJpdCBR$E"
    b"u_UYfK(=zgwQOFN%LE)KmMp+rKgj0V$@BOi#}a(=SZ?`0!sR4<-hj^m`0Rzx%kcRre13%eU;K^J+Tw4XhAV|Dh3i?ko`q{KTmh=z"
    b"=!0t?T+?t(!?ho-{c$mlr~q^-oq<FG2W*3n6FxKG142_n<G!w)*t^_&K5`=k`j`g|07WKmT%Fk;-#V|~fPdKl{7XJM|NVYwcPGJi"
    b"FCGUdR}wbf%zRwp^HGlT@k9rk56rytS-9_kPcM8reCF$q>{w#1gNm19wf~h<E%wWJKQKpsD2V-$LI1IwoI7*!L8gJZ`hz+4N9?Zk"
    b"tM>q&=GVO#E_cD_ZuqQ*&szAbgO3WIuM;*ePJpu$t`4|5;A)4f9j-RG+Tbd~Rfa1pkZ($G72zu8&kKjolkoj4e0IU-0LhsbpBZ|c"
    b"GY{-Je-3if^5*Tpf!yC$iRjJ8KwE5nA_+sm6L<t=t#$+F+|LF>VeNjZm+k-_>OR`>hF01fSR{}h?%mc(*1}WgJCb?7R&p=iQrpw3"
    b";Y#iE+5Vm4h?72SV#Ju5<{3#g+QgGGn<?MA4Zi-<0raNS1|0h7#Sa4u`TQI~cv?`nlK&JYvBEl?H<{P>x3i$s_h!P^MckA)2eW9="
    b"@3k$w&f5M8?mC8t4$Fe;R3}h22XoddRGyjHw|NTRr~VtVM@60$vK23IZMLu%y?FjTJ3rtVMK6`1TNk{CP54`DZ?GtuRN*fC8A>G-"
    b"VLu!#;g9UnSH7z2n)gYCK90LIr{GTmNMwXo`vh>-Mbiz5=6*`*p9s*uo0Ne8-*wl!Rx1&*aUET43tiT)HNzX$n{(OthzbcnVu}{h"
    b"J$UE`<96x!tfpohp<b$#F3LR*GMoSJviW=R@;lziwKuTe7z)P@=@)!*r7CAmM#L>RA$kWte<wu88Dd>JM8C_^GMjXA%g59^L-hGO"
    b"vRO|pWII*xlwtZtg)t8;R>+*&4F9bRn?nD?Wf%bY*?>tSQ)8aRlKC&`g-XB`n}Yi@;O@k`137j*`9`IXEc_{Ooyx<N!qYFnO|ozo"
    b"d>=lHFJ6YbQ-|;_0e3H8mc7m#4>a1l_x64Fc+1uAHWBaDwgYmL=IuZJ<^H!@`i_73DmuUG(>W^&$8QgZsC@y0wgVWU9pp$HbO_H_"
    b"a|*`6cOiP;f;`CaKYy^EtSfVbtUrctR#*G)HMPv4tt+z`@rkQec9GR(Wf!Yu{1ps!1bM`vZ7nNH$-q?01RJyqPh^?A?HxQsR;?g-"
    b"%(Qx&hi)t&zak#eLynZwJm=3wk&K0oI?8*^hs{0OMo}B9!6P}B+U)t`h8o-_5Tx&BX3W}7_>Ygt<X51IT_hisUk1(oBT{V(hZK65"
    b"?TnUjXX&zXYVP$UvHu(HNR?Y(85Q)?JK6GOC&&3nwZm77uiF#A`pX`ba0sYCwg2AQ&JN^WT;?){90Ym^aNO@I|CJV$p<%VmX}p4T"
    b"_tElS4WtY{FAo66;)1I#9$((!l|TCM-<QlSVn0t^K$88r6fwwuI4eYh^9@}8g%2PK&|pXmvWx@Ikp0<Y?m0LX3e%NKj4fk3c@gF="
    b"&UE3aN}x(1c76)FAX3G#w7sQx7g`ga##a$o3oCd9PtV}e@AQZmu_p`hEoP(h@?Tpc6X=C2y8hG*E*!g$zPKKie5#NoXtFKV=|ZLB"
    b"Qt$Xh!qyMm`+m`eu^#70XXn+z*r~~6_Rn0+)k0iM5b<j`3#eaNk_AYGVtZUw+b*Ai{96xlq@=3=OP|~cBps+@;h8l{a)aq`z0+ST"
    b"75J8*f(AAdC;+486lVB-U`ZC=ADTA|zN6HN@?)eDNaT<C(T81mzb_PynCXpkp%V^;5w`7U7!s(NvyfD2Gp1A3l*P{dcz}$+lRsLT"
    b"QD<)A33m<T!$T$%p894cn|d6UmaY9nG(?ZiVv?zEDippkGK%gQZ~WjCCX`0ZFR_yH+?+Yz&AP}!ff}af><`K~np4*f<QRT)ZUmMi"
    b"-F16ToiO@mZy(rIHF$pzKw8A$z@w}?YT-*$;nMUJ?&oaM%pD`+)uy&ftJM*0mp-S0P`$dc{is^lEvPATx3IA?;!@}bwa6Fu!uM|6"
    b"A8Tv{lRs_uuF)6dD8a~dg?>RXj%}`vxFSN3y4kZ_S)o5F2pbAxJ)pIQLm<rCA}+r|@2+L%f#f$fWT$dN<KO{@!tA8yh>3o98*7js"
    b"{9Ibi7O9Qzd;ly|{QQON<O?;;9z*m;)dQuVl520zZrn8VN5I}N5WK$$VHgU~-;3QSlLAS#MT?+o(XXVYbXa^lik2)@Z-6CnGk+gV"
    b"k>mK*AA8TNmhcSl_H)ak=W$J}YG~}@lCU}ki(0pL2wC0a54`9)c(E*cc~t{f<d~kgRQ)km6)hQ6aU3Y`TxI(WsEX4-Rh(p~iZWLf"
    b"qutv0l*5Q(9-kV;!xG^R2nDOtomi?CyAxUw)*nqnhokM8J`V7&yXSl=|9Wc9r|~aTz8%27wth1I+UNilkjuZ+fwzOWm-{c^UYAme"
    b"=MNh`*M5QgO2q(GxR&oxkV`4_XUiE{K+TJg1g-!^mBwzSrUdD8{19DCUj@p~GRKlyHiEl=t3uC^H8l*+nruT^(_hN9LJ^tHbu-w@"
    b"Oi-F=h+4hy;-B3a&(FYlWaQc{K%DDCcv`yiskQ)<m#uWKp9$Mv<geRLsB2(a?Crl->&Zu)LXBks4H&4QR^^7Gcn)qVZCfy|B5DoQ"
    b"2j~KS22i6(P>gk<E9eNH#x7!xFP>pyxA5go;93n)#BBV*NB0Fy+J!vGBdK@A5|XcC#WjnB4d-H)#%>rByHvKhgf3^l?^MFvyW1|k"
    b"4A%{%+b$vfhL^M0ONqT?{;#Akjz8czS493(-*_}JOZfzXPDH<bBAZG_vga&MVe)B6FLk}c5B#|10sy*A70a%s3S^T4Z=CNiYoT2)"
    b"6`4$b3%6Zid;!L}4x&dH{)KkNGG0>RCHa|dYKcPW)l3b;`op%JbpaiC3gz@*D3&&bt=nH0+3c0XD((h4WwLJH0|`&bzpoNVi4DI?"
    b"?f6}>10brkpZ*A>0S6>#aSFFhq{N92?Y;P*#rr-o4rI_CKa0nhJ&yS~#bx1|Ky;5AM{$r>4I2L{&&3bO7NEA=1G0z7-F~W{<yOu="
    b"gW6Cfx44$Rh&HEJ=-DbE{!7ep{`*bee}><(9>sr#w^(tkvp9BX!KPcYFWDxp(l!|2QgSXHXQ^jqM$G1Ofe;N{W`csTnK^ev(7B74"
    b"eEDMrLn^jkv*^=ClQZ^HXFqN1nKMSRr<ue$i*P8Fk(qHeH35Zw2Y)WRqV1Z&?3K4PY_+MW#-fb>W6tP4h8?>TLq_%qRcFT+DaPZ^"
    b"KXru0!5*hS%1#WPr_8FyA9SO~K;kFY?%=KC$;^1v*5i4-zC7ee^;{tL4C=zr+<3Ul&|W~sa|1mZ^#UMUg%hOgP4{K<8ANT@1Ayq|"
    b"o$)v(D*-<h{eSU{7(>Kvq~>HM=VzH=YEc{X-D~6V1w&4vVZ{va<gLIlE|c)d0BU{`z{3jfo&k4%9!#@my!;tB-kbXL^=;&a^-bq3"
    b"=ckRzv8(3j*vL3~>@Gu9+Fimq=T$K(9Wd+|v8#nqzj1%D@MR!p$k(A9s6G+n7Y}~Ej0+WPS3KVk-;B(HzkT3CT<muKaB?~~{;XY="
    b"wUi8|$8r$J?w#ysq)&9LE|U!x&X|tkMYCR2*VU-g4G+#AVpQBPCJZ9ydy@HWyx7cdr^YwN5~5nnb1$rkURc$I`Oc7H_p8jy!@N80"
    b"Ls`d;dWziH4|%Vjl~S+iJY$1f8Ey+wJy~B3chzuDjp3-t{C);-%5X5$F&ZUIkmw%hc*q1o-Ex=)ki0sId~**o7tlzMDdDylw4XmU"
    b"tZD>4f(gCRRJ>L1xUXRQX?1FcCDvUq_f&LmN0k{ZUL8$(tP>K{w^RRtr^qyR>^XD&`@jH}=<v`*lK9Q+=Rtt{dpE+ow@Bn7TQSGY"
    b"uac`IDxd#BhfjC!o4-WgEUMztr9hKASLK=zV`uHbdeG6XVZZML(4WSnmQwT}_dHb@U@DuZ2ZX1oQ9I;1c}rH8S+fdewX1z!bQ1jz"
    b"WT!{q3v&Eoa1Qs;T~7cq%#*C!@#ni@i5ZJ3c1!?K;`eb7Oas7prvkfW=g)Y$t?mB~SNusd!JXJW7kKLV=TR~ESAg$ScfxZ}tH4e@"
    b"y%@eWJ=n3hY#e~<cBp84NAdQ3>aFesw`_JS(mkD<?Hy0dgDToy6?d?kN>AsevmJ{}u{{Ma5wDT%%zMdrUx8&eoC(vlT+d|fXmh54"
    b"W}Yg18ZYj|(>2(EyYNeauhgig?&eb4B>D{~MfaH)9RBm>L2!Vyf8uHE_+p-zJJPr_aQ^v!b?cq)iSg&31(0=k1@b2t-;9nr6AbR="
    b"?BFagw$UB`XD8&5c4h|lrw$+Uk|&~vm&AT0#dLAQD=?u`lZDuC1h4Wm!j9rEEfMlPC``Wf<TVB`<1tJ?1-S&rM=B+)G&{yKH)Wy@"
    b"P+v?I;((cfIej&1<BwRse!~nVmVK0;IE^LtN3Bn-xErl^nKv2zvv4&E2k9}JZ*uSJ*wOzl%ws^|vTHQ%{o5r<_&tW-<2S6H*WmT*"
    b"@Hq~jx8d_Xd<0PxO=8Ypfq7>*AC>+Urh@^2%_ST7py?beAC_S5ZD;Ku34vZJ1Qi2c*(UP<3?m$JCw43rU6mC$s11F9lViF;w{XG4"
    b"%>l$5>)yv~*B!+$X%otO;#);m)h-wOk#jtn<RA+r$)e>UQi}azi!UMs;*XV0HREqVL0vQ0c|`$GeBS{6XDm-A<Z$7Rox96Gb61|i"
    b"!YrSk=Vspu{ZG``OL!4i{M%)&0yZKj;wL59GDdC|Z|kS6wTQ1SV0n-qI`I=*6DhvXX;QE4*nwzQ{OS&N?RZSY9_-jr>4ybz%Z1JY"
    b"brR3fw$C+?r68N7sJjiXLM05D!|ewRjjOipMKHtk{=^nbS8Z^`()Vnh*ufCI`1Kv^+HtsTk88(HR>`fg^nDwq#L|DW**Unep0+ct"
    b"!A%+MWLh!&&mYlCOc)ghe&5KQP>erdXXu+LC{CzFi>%L!WvTQ044$1;9TrUVS)UfmHhf4r0ZI)>RsWju8*|DJ<9{We<bOR|{O9^#"
    b"|8B%^{#QRLK#b~bY9c*57MG1+Sk(j#;O@sWQhNgLapr*2MGHXhW!M=p1r)#@8EUsHkpe%UWEIoNF&q$bHO00<q39@3&jd*=Vo^0K"
    b"VP;o$#VSrtg7x285|I@8<r>y0to1MqtV3KBJ0%Ua|Nb@pVaKz>`-f-zkWrVZ&vO6pkKl1<C48;Jn;-s}{$Z^A)BVGkYk2>#QQiud"
    b"erU4~K4;-`8a^lC^9Fnl{P2IuKg=MJzyZ&I&jR=;&;D=thhKOu>mR=NxsUY^?|PQa2WH;c1NRg@w&y;<Km5XTf3AO+)%h3shmE?|"
    b"!et$NRQPO#&vy7c2A^-k=ZDYzPx*&Ad=l{81D|8?Is4rIC;nlS57{|2@xn^rzp*Wn5cRyElLQc;=^%x6+_YrwUiHIiRSPCe*w^-s"
    b"tDsY?`r4_yM-W1fPDnU)>nn-WmR`Nk-drujDs1pAJPKMss<c-x`G0788~CQmvtc|Rr|oH*k`!7fP^3uEN&%|@Eu_^H`-K7~ElqGD"
    b"xM!~Gley{O9MP>nY7%X76U9Al)8}#T?4$o@?AhK;r*1eWB#oqe_yJ`qiX!T!rweESNs9>iU)Ob?lcvDj^ZtMDA3e=E_kG>pU)Ozo"
    b"VwiV=Vy}SRNgyWBHr!ThhqgdDmt#58n`;hAC!B4{r%Tan8D0b4=U0!Kxb!ZWU1SGW7DnZKHM?X1WazC>sp*8b_TCFk-~=1R!u=GC"
    b"<!2y$$basLXZ?J#h@)4DzYw&((5=kn)HqJtktYPxlG&}ST&D6A<aZETi=THN5!{~0-R9mq9ng254B3a)&-LajE6^k`nzM)v3NGcR"
    b"PL)XtF@NIhZOA%@^FvF^peb%R$<w9t0dW{xK=19OPc9kK`#P-_ID|{!k8+KkQ@Je|qQelYepH^0oSPGU?L20SCV!_x3B2(ajR$03"
    b"*@nVck0FwGCv?n+ULMz;F0DmkS-P|ae(*G5tB|SJpYy1StMyDn9+G?=7dH#;mM&!rNMh_W!G3&gDT&jH>3ym+8V0UQcFxD@S7P<Q"
    b"&4;Sffgv>*(#AuAhopSvTGB$lHQwHz^O%M;5?>nw$JXClq`WgNOI{4Vmt2zd&H2|j;`ZTnW~vr+ElSJ{uRRW3?>{O+7cgX5raW>f"
    b"5`mq{FV7MNz;SZu<1TAOFfC7TE1&7d;P7JHpFXm_Jea=6<nK58KOG7IWD=R46&60vDr|=U#Qb0>-U0HJdAzE~HG%WH#MSCnevN3D"
    b"f+X2v=D+~ndFpUxt^2OZdn;id#F9c=JIrrgtLoxR64>G7jcv-6%hh!Qy>`7V3fF_!5ft<^uzt3Soniai#}L+W7?&cyQ~BvKs@)uD"
    b"cO@2mNWPg*OHXE6qQ6dQ;f0y1tgm*SCFdrTxmuMQ#%2kPjg|AYRSxejz<Vzi00AEK43{o-sD;Rv(i(<VP4+17FUhd;`nZ@nb@Q6l"
    b"EUtF=QPB<g{cS3-6-ux(VTMD8ipa)Yy;P%aPq7Vn^TQT)BKC=(TwAWu*)a=9epyy^cx@W6Hbbk=-#)guh<_YRNw-3>yQcEt<9LpM"
    b"B_6#=E3pDP!sJBssnw}0;1z*1FYz?1Z^3eZi`6a~Eg0?&EjX=5F&sV_OVFPs`@UuC{pLUsOr5O`a}bsAZHKn%rP8gI&}zXP_=2S5"
    b"MeDiHxKI<?^Mp|A=O)9ikRSsg@@3uUkS!*O-RF?jA{VtQ$6VUhmhV=4{A0MuM1lo(u_lpS$Cj5>jYORKCH6C+iJ|4f#xjqyT{(po"
    b"<lQ1W2)CIEXjqRS>Gq#ZOOx4~Y-j9C;zOH$qVl05LU%G}TgBAHx|BnxkW5}fTe~uW^A8~t$f5+&Pb6!gh%b6v?aHH8l>u-6K(atv"
    b"Ocf}W&hN#z$(7KZiM~t~Yanj*ZN!4?KDrceQ6yQgKU?oGphH~SvCvX$Ih-zmLp`gkjt~zw2P#FHGnGjZ|H9O*g?!6x1NJ`iW)sBu"
    b"&Qx?w@SVAL(>U|?c-Ti&@*`$E8qC`Ru?qN%jR^jcJV2^z%@4ku2b+>LxC-u*p%vB!c;>@X36B*X3+w@9$bpCVIfIV?Ead5r9`TP@"
    b"%n#n5ht&-CJo+NxI$bX!3SqUF04cCq2Jgtz@lQQ{wrigT`fSoZee`*)_9@b5Wga$TwtO|*&pM&etx7FdE`r!fSX7Zbgh%$@9%1+("
    b"))ONJkLP0j_C|z1L{`-A!)6Q~h9Gz;8+<dDXL&^=Kv_DKK~c-H46}Sbm#!bw+QDDuayFxR`+<nb7iqY0AA${T$yGbxkN%N)<_EiT"
    b"c?bNNcfeMy11!{tZ()hoUn5ueHtFZfQ;6TzZ}7e9Q%913uH*Hq?Zs;Xb~3ce!Fi*p2B+R9&18>SZ#U2cD~F;{J@j^He0Vy{vSu}>"
    b"3qk6*+vLFya@2mUpwjlKpT1XlKSy)a_Pp#LSzvzfX990e^`EFcN7eTHsv3Gq&QlW&!()K}X<=q?KH&OocyYSjsdO*rCxI9|wqYI|"
    b"538V8=i?fI=9LWEpbWU!chWt)gC~UR*{YXm6#+Cs6(N*1P!3IfPFloTP*2E)L!U~B(nRx)N?0T%P{JHczyH|a0VDe7uEY@1jDy(0"
    b"9jNS5w`Gb-REN{8gwyE<2cI_TF49IE`t5iRMOGYY5o;BG0q4aoek~O+?_W_@EDG+H3s}*kPyz<Bx0VM7v^uevWa;qN=%fOF)Ic%v"
    b"P*rUI2vY_xhr)TvE!im{MG-oj6dfG=WK|4+zcgfZ$y}&Mcq!E)6|0a+J760q*ZR35Bo4l6paqf%3t0wVG|&V`Bkww29JhH34A`m="
    b"9;eV={~kv$ic4uj0WJen97>wyBHx+s$cPD)QCoQV$UaB4GWDxv1ggH2IlqEza079|8gzPKEbnkZ0V~l{4~n-TliL4EN%to{B6|ZS"
    b"G7e_!DmXh(*bS}AKvClXyB&wq0FLkH)!;7cs=4w6K5uC=fn0B+YQsQg*~S<gd`r(q6Y5)yQjjJGf+zn~`%bRGmWZ6tP=ki|2+OIt"
    b"9O+nUI>dOk`lJQWy)}sj>!sDcm<uHUP_?#asdZ*@ss<@?$U<H-+SgD@C)Mwh#%I>XQ(W~a`7fz>g=9;`9n!?iD1Jx4xrzpkA5SjM"
    b"%rO^FLDHO$Cud`l37PEX^T@}O<1@L;;6b(lguEm;uxUyctd(^o!w3BXfC~)2>w81bz6?Rlk^(w0fcnWs|EDB87Tmod??vuJ!~gLx"
    b"!mzgr-=+b#l9Xw{dMn?mN*FTbQGj7nE_=Q34XFW|UHv#yTH8Ht81znM@FtpaE7?H|^2e){?;uifW+4{3Q82Eu)@Z0(PZ^SQN|HnZ"
    b"kNk$ps8SrMo!E&b(s=YvD+G_p`7MnYkkC~_%K3;*A*G!<8QMBK)vuTGaE#_AC#K@+dsVU^6*ovl_+FvO?ID#N%Cc6Stva2Gn_xG7"
    b"o^P3Oays1}Z-sIz>HS!ed1?%_#EKiL%MCEIVN3lX2S~+X+eyU*xtPa#yw%Ed9)$!gG;{P*E-3gAnd$^2C~{l6gXO}cZgIBy69(mW"
    b"O{#0-rCB?-iwI9EoJz5p+uoaCZ%FXQ3R2k^P^|H<^c;?#0T<v2!NbEO3_?O2-LD{eK?n%cqrBDK?$pvJdyo9yp}XT*IRD`}0Z%P_"
    b"H^LK!=Nr#CbUPvJFYx>Uo?pWAF+5X{{+yGe&*A?JImVnEA+kjGM@VCbG+W{K#^+Qx;cNdPY1=URY20!zq-%bGKdYX1=$wCW=uSdd"
    b"7@pbi-ueRn&4u61@Y@2<_W|xY`27Yvx^3`S^cI6<^q&#`2$me}J2y`hMN2-u78IH+mLkhIi^ZIE-vmsY)e9}5dg0y@R*cur9s_zK"
    b"gfU$lDozqH(&bc2PLc5gG{>KZGFl-$cCsn0yWoC`mr^&|xhxp<Y@7wtq5|e*IgD<J+ta2*P;e(#6;I7$uPqDi-t_63tZU-f^jF}O"
    b"4APe4^fGVH^|U#glqF<>X>1-JYk6RGndpxRAtW|BzPdnOPmLELzJ7$czKUNwp3-+*n1KsXSLK=lE|ZG#iB7nmr4ZN0{;~I)18?He"
    b"b&B@45g#)L5;*<7%#p{1?iE$TfhcT*D%<%g!hB1dEnfj!4&EQjL(5md>5rtX;9AV7$O4Etn^ppUjqlj^Zn!*BvLyDAfvtAdhq@++"
    b"Y#PPS#dv?8$(Xdi*7Y&o@tBTnTv-QeGb+#OZ(8Xmb@P=@ub3X-;<RFD<4PzjQ-``O8f^DJhkZnY4g7Q1f74)t{~R`=!QTJRVIS6D"
    b"ANc36KStO*fDQjsSQiWw#S!k46@hpL9M?;U2&4*(q5LNoS!Q+RI1uAl!oEi;j+iz@Ob_{^CVOn1u+So(;sN|iGGypfMDG!h9yI<R"
    b"(u3fHHqn9%5OYMHj*Ax1LyK*ogOxPCi#SK$%$Q0P)5o)25V}|?>TtlU4I6B!K-42mtF4ptP1zD>;f4ZzWJQ5K5S2fU2rmevsL^&*"
    b"HE<G4g(SFlEI>Inxd1N3r(Y*(3!94>hud|50qI++P#ecj-nqf|Wu4U6rkIZsWGI(3NAi^&YDx_l5sHl9Y0W6@!ygq+K22!GP<X{O"
    b"oiQ00kbmBb#W|I!LzG8<4t|c>vD5|x=?xxk1@B4Xzj0wGR)^Xt{W(1lhT%Rm5w-*0RN{c>bRk*Jqui>aGZDEs<$%RSO!vE#=47TX"
    b"pdF$z{2FfuB!g4N)Jl1jJmhSJt%2;h@w6?W1$RRUYo59j{;H%3Y_hh;NnAqH8a&2rBXdh`cy_&nV<6>+WN3TnPHUO3=2F=mZqYk@"
    b"r!SRi0=uR8oRJ)O94CZiW|J1fFinzj!(z|4CWrQ!6SnkBY*N$7yR={-k*jN>EFH<VQCLhG79Bk(X9-9FznlgBeQXIlOUSQ6%7=R7"
    b"`%dS}e-7-HjV(#EDk&tI(mLA!-l_q!HwREkJS-w~4ni6o$>S8BB-A0Rh0vE3X??iNw%d1x-;v~k@JhX-9zLZMR(4h@rk4TjgEH^c"
    b"Uy4~7Y{yWL)iw}3WPY>{%iKT6-dPenBo)_FU2<17vFSG~2~C%W!Xni6Hn?OIU}aW7Wu%*-0*wGSo4wQhF<nIc*j7Qx?-|F;O^*7I"
    b"8T$lY;mt9K);W2vr@A>@E;A!gI?pjk+UP0Xv&@VVxb-xKA@krDXu9&4l-J)#(^VB)W#X;%C_CA^wGCG%o4X2j6}K&AI|Lia7B0Rw"
    b"3mvdSuAKXpEKa|P^fz;05`2=;>8CI;F|vP#{h5+YJO!sUb@;E-v4k`pu48yFlZUmJ&#Dq$-To1W7p|{3>DyHus?E4i&@sz(9%Y51"
    b"n!<$MypmQ%TQ(TfuCPscn6Gc!A$PiTB@*P~bPTIss+6jK#2|MD56L30zO+iUGGM`Z2{UIz{T-@`JJ^t0dG}K&S;3Nz$>ZA6rOwf;"
    b"*z4>hoa$#)nr0i(G&uy@IaUrfqpx+e1yAfwAB={w39}xuk<rg#SjkhBxqGMukq0n7v;YZW_M!fqihsR9R{>r4T*11Ti6#N|7^If;"
    b"tj-B-6j>2M`4iUe7$&kGU;94NhFiIkTF1gJYm@4$t-;!Y_`q>|7bEuy-KSBU7SH*}9CH`mJuDbNgySMC(!OiM-P^5@JFo7(PtZ3P"
    b"RyHOrWu*ua%JuhEgy=Q0g^KT6H$CBi8tSNqD|65)$V7kC+TF*a*M8WG&_qN^2=>0NrvRtpc|j1Yq1_}1owCO^-o%#a{HN2>HQ~Ii"
    b"dZ~J=C>O$|^-hwim1aQaCt|0Oau_LzG9iM!00|<(mXH{p)Z-K|pQdL2PQgCZ^#YsLiQ{&R_g19gm@YEEn+e^BK&}WLgHG+1^R}hX"
    b"eq;gL*@Bws{^%)Z`T#l^OG~ponS!U&(HFW7=TTm`NiaE*W&RPPJQ3f;q=^UR;E%7TNoe$+HFkw~3t>#|P!DVWD_rf}t<26r?!>)Z"
    b"{`jc|IJ2e2UdgLhTobrl9qwb*y%>R}dnL6NZe<4NJ*7)aASjgE-y~p{a}&H7$z+nRaX25FvRK#eC>iSunCnk)>0~xSC7|=64^@{w"
    b"tyGJ><40?84J)E*xH8qSx|M(D^3c2*o=iQ`rClGYPPe@lrM;hkJXxVC{{{I`I$Fm)l;u-M-3FvVx%z67c{UTB9i2dNTMZZbGj4Nx"
    b"+Hoi7+?H_Y(z2-RQgpi8RAE5Uf3FvEH7nV0a-f7ZQZ5bKkb4|QU!JHS;yu?Hg$(XUFTib4)p*6-k*yTj-6sFJv^38yS*=oKWd1$O"
    b"^c<`kv=HO(dQQ;E<2&_40(nkUP(CQV;yE!HzvJN?t~F~y<rrJ^4n_){-S-JtkZfTt6Kgdsbcu2fZ&jP?rKQln$pZBS&1T#rhHel-"
    b"-!<KGYoDNd^;P!`S68pRp}Ly;UB{+>#co3x$zcaI(i}uYHPkr58ZG3^c_ehhS8Sb$%w?seZ$?b__`4n!bW)?cJ@Q>kdd0)SZL1-N"
    b"!l-1sw-%t<lwWc2bcl7gDTnDpgk)YlYj{{xzKORT;o;B?CP*tn0*GSsA5QjeBTG`;XF;+QGxw(3l>f!k-^R_LsDsi@x4bJ@eYum>"
    b"mpPUDR3K;}iM_)SA{C+Ln=0=v&+0_QU}ZWo8h_KaSfxrLj}zCTlBdgX>~Orhk8Z^i>Gr9FXL@YM?4nfYkBW_TLsL=Xz-~H*apvH^"
    b">vfp|&4K0m^Mvf{AfWp+mTV5(r6;1y^XPvIu{md!So_2*vGzX`2$yT;?_4hU33?}Sa1v|J#1V?>HL`aio2}bOy2RdjG+7UKt2SlR"
    b"UJ`465eIgA`4D8^Wi7EqF?SLjRz;Lyx4*cUJ4B$ou%$w;JNfjEzh;Z|k`VF5WqaXP!I^Wl$L^T=Pi5m92pZ*pubQdObtHS>2*i7F"
    b"uSG^KySoLg&lGsSNSAif{=!NqbJG9Pxw5f;S1X*?kE+|Gno$;idp_JQ+-$*P#9n@j6`}l+3tmb~;H5SFR__<IjlDJMf1b?s3oql?"
    b"quV#Pw@k@Bl8rzYD}U&tDGzV2()1=^nq+R-oG!(}Lh~swDJoa|RRf;R=iO>G0c=uFV7)J5AKny10N6L51b_?U>ri8J?X<dmlNRgN"
    b"Pn?Tiv5_2qwA`uK`SyBS+#jt_3%D>nDv^#OaFYhk8ci2V@lVUUX>55<{*&^`FDP$p3OejL6Wu<vu8t+x>u_SjxjlMlry8~hdg)TP"
    b"vQJa7y>?Wce2#rosZ6;NMyFqwPyXfTm2O(3i8EGT-L1@Dlu_DR>_4ZMa?r~76gbbOF49CR42qe*+ef5J+=_vJKntGcdOHQ$$;d5s"
    b"E?$TtaQ;uGLr+CaDa@lJNE1ArXb8iOYW67O_G+3vP+hd|7^nKMCev2GG;6B}SWA=WR6a#B>SS1N*6^8hI@DycMMJr&S-bPjXH1W#"
    b"w%y8cb+*N!c{{m;fm_wTqpq64_wBLzcU-?oS)kKcIXTo_P<rYWhcuowS)9rUSHvYR!{@6sas6k!1vHt+GP3WqL2mjLF?_ElhHn*M"
    b"=o{xVx5eXZRf;(O%ia&*@}#XkX{z;XXthB6Wigb?Rai|G{=I1)r1@*iUBlv}Knf$2ugj9ZAo`Xq<u$;izr=P-ne$aTO*+&_#Uo?+"
    b"8@rzKld3Zlo`Lq=5m;%G);QhDM`*IQh$}_I`hS+Sm;!sHtNm%cT;f#zs_J0D{Ft6bUd7~KS}sLFQ|OTXOr&fmR9Gp`{r8aR*{|rN"
    b"q8c;-UikpbqRC$oy%(u7khx^wsK3gR@6_pxfa1VSTGe+xPd<Ro@v{EL5o8XL?T6<2{>CBriuN~tu~F}=f4_0)J$dB4Wh3u>Z|MEo"
    b"l=mBz_omgrS@6M;)GPHD_@eGy1yS7m1X^<JbPSOgP6PLLo&%@WzWCsSqc-1YewerCI#qi*(CBYVb9+&wvI$PbjTZCvabCftlyEKm"
    b"<T&&8iM?F3(&;~ff&d4?MMnTSoQv1>aXq==iA{lla7;eAI-?I9o<<OO<uxtZD~ak2>kGKuLr^0{jQ5@Xwp8Rh-I$5~EZmZ2`&xXb"
    b"tL1!n#TRL~rcBnigbN&t1G{@f)XLy*sFjhSPra{uZ(66?L;8&0?Pvxc2E>VsdLmJNsa5B6DTz8&yLAO=@0pMYX9=|kB)tQtD4cR7"
    b"txn~GI+e_dM<jq0Uof0-zpF%bW6am>L1~T}7g}@FLF(@7h%K=cW^RlB6$B9@ZoMt)YDIJuZppuh!tLtIx$JH8qcP(?;~tmtTVCK&"
    b"RG<R1)eCiXdr05W|4IoibpI=rV=K@WUS%yqdX7nz1L?9>1P)2l*d$vN@-{yjHSV<S#=>GQr!vpTWq8eOr~mX^IWN(un;U7=2U8oz"
    b"g`N5y3m;lXk7yfUMR!A&29UA=bvwZlA+dv%N)Xl&qPrGa=`bd88(Fid$yZY?-Og?nmfV*!{7xcwZj=A?9bGfGO%Enr!-KIeb68(Y"
    b"nQq({&NcM)<g(b~FW!Ob&!^cQ04xB&?{su@AfVv_zycLew_Lx5?YvN)>udU7Uq}3?r8s&>>w+;bz74%{ZZ3S);BY|ixQqz^y@pJ2"
    b"5FHM%6WDJ{RW;|t`CT4fiu5z0ouNW4a*bfC6k1?LPi7NoJaIJl+IPzN2|=t*G{Dx$a@iUG$Xq!$VVoQJk)9mlY%2EZJ<89ySY9Hp"
    b"x;beujs%ZwT!z69K=6||6cE>w$L<lDgQ*QRl%)woC1Ln*GI#i}{j)9u`>frg+=4fe*S1x|KeitdXeK66DS!(?#V^`lxYJ^fIWj%="
    b"hMlIL6<X$mmaV{9dmkGAve*V-zTi}N6H~Jj&NjEA=g=tL6RA(zcH2kHPsIEqUv=5+@eNnv5~r;}$_wW<1)}olMAJEr|LI|qSDvFi"
    b"*TV0{mB`F#L3JLK3y0WQbl#O{v19eSaLc;hKhh{I@{e@LWvbvCUh)J~Q6D_Ztw^X$Pzx?{lCwgAjjwpIaZRtC!ZCF#YztR@#Usx<"
    b"k5QcK5;AF_;;qIL<QcZrt^9mHl{I<-kHvqQ|1thE2k@V(GTRFtCYWEHPBmBHRxZ6d3lo|Z&tO8c;}^$-_`mL><pMgFf5JKke%o!w"
    b"-1hf9sC*Akg<Ql5S>3N7P@HYHR-*@}7-BfJgxjzf)E2GDut|~m(by++45u0<a<Qy-m-5wYUco$LBIOW#=D-S^eZR3HzZ`k~Sg+tA"
    b"cGmm=GJIgNRI)d!UbF9AR~a@p`%V|gMaYs%=!%*gkab0m=wSO`QdCy$@BR|qNp<aGLog3;l9pGUKsqpNf&fs>3~m?A%@Tbpzb_yQ"
    b"xL>7q<4_v+*%L@p>JnLh)lPeSZ8z?SI6IJ`y_rLn!LH@-kL1W!Wq&Nwr*F|K-s)6li`qj@Wln4q!yD~5tVc0+i$j{=+n}3rUdJl;"
    b"P=1K3DL;y7!*xL(NQbS8X#pJjB=M&Pyp-S?EpLaet$|orF_~6ND0Nz{bvDTtO(FtJCcSvxdG8^#Z^mp*Rx<E7k|jvkk6fP=bAdl|"
    b"5E*YIX2*(3;F???q94HRNJdcpHe7rxBzq~(B{GikzXv#nB@<p6X(~a)HkSy*p{6oGag$S6EyedYm0_yTMlp09VuBX3H(g{XCiz2^"
    b"Imz+pG4j*U=BsfX5*BNbE^{mGr!<V(_t(!bTPn=Nc`?~0<J({#Gns$4$||<I{b!DN))xm4-6Q(rX8*@S$()x+>~=27ui8=&y}sQ("
    b"4W((<*Lw4nXOE-n7ZlM}1gCQHQq2xSzB1_qx3`~?%Gh4O!}hat*_$q)?{kQX)#eqQ={JeEHdPZ^9p9!@PS=Dg!<?*~80A2>yS)ZL"
    b"dlwv6(cbMwjvWKu+v#C-cSB9v#^AqAi2s_M$_>wF5L|tu|6EDeT#gL0l4t#W6|L#Fc^cC*E@kDL(6Ca~d{Dpedor%6VYpA<x(0Au"
    b"EFW9D^L&S4xK$!EPj4Hr9fJy$L91%NDNU<gD~+#RFXgF}@@;ykcM`5S{x|eVaa%qfb8i^xNt_;KTf+H)-R8hE#5Lgls?6JW`(tnV"
    b"PcJb)7$C9#@Z(P(Lh-ntcfrqAgZu;QIsd0$nGD@;pj=b(j?^nr`8MCHzT`LXt<CqUBk2qd$T$88%jkYX=K!GVAz&d7_%yvEoledR"
    b"9+NAHy<@6K&VY}p{KJwgfte*2`Chdo3${9BB<UJ#DcqgwGxZHRaa}H@-KM1TY1EK|E6^fRbwxSr-5a##_u{f~JVlEK4(-srNF~u+"
    b"66!R^g!Dtk%|a~}82_KW>(B|%*kkZ}1fDP9`EPi(!}A6_&%<MacwPQK_@^K9WiSe3zH@R%-}C6NNb<uToN>0a68lV@bI4Lj*>`fm"
    b"n$gK--zn9=WRow2dy)M4*vl49!if<6+UH~MOY!6~R{LzS#ajbsiL&YS(NwT!T&3N#u7<2<acTmRUeuXd?T=NsI6XrJti9TPRw@nM"
    b"C4}xWh3*nVSBCB??{Bu?<_B}O`?Jh_cogL!i+34wAMymvs>h0#GB!E3>ZKVeKm!cY6y@cYaJNRXt<v{W)|rqo+@abBgQb6cmcJ;M"
    b"^7L!aH0~r`nw1r!k<nOxwlM{~6_b(axc?~PDCIB=zxUZvfju7F*U`=$oQ~yEA)b+m2I~Y%vIw;VxTh`a1YK&U4{onJ9kQvrE&xkV"
    b"2WvtS#1+;Fc!C?N64E6tQgMqpxQ`1Xq9L(pa=iNHAZa{&^PzB=KRV<esWw0Ow1L*$V+W7Wx_bqFY=@E)ULp#w=_TCIVap_QNU>Qu"
    b"xcQSt<fidbzC9t;4t^T|UdAb&Y_Ee$ux?YSWU50wP{}d41mh@!g>~4cn@S{W9iI2*;5>}NOp}+?>2gtGu@3V#2T_NdR%bHjWgLdo"
    b"PW=uNX`I9stZb!~HGlZ6nTbH3oI{6JDh9_fVtugsbvmI4Z{aA`mfC5Nav@BQAQh5G(PFYN731MLokf{Hi`X9L(sG5e?L{1UJX4gH"
    b"U(`<T!i1)BjjJE^qR}@G9OCV+Hk7>FN~9y?9gWZMj$~vbA$3Wcb%(d9WSqvz^A)*~y@aCf6JX~lME+6%eTY5q7cL~iWjY;P^`;_1"
    b">D#LZEUgE=5U;F7i`7$E3E`HJa{3AH!h67{2H%G*Jq?qD9zd|n!AD7q(j3@KGSAjI26F(<d#}NZ{%K~YY9;=&Y1ypogo<|8APOhl"
    b"o~#FCtlF!0x?$?o>Xg&DstSWV(br|Io+6vu-O3l$8LNKdkvZd51}Zc=fbulA^4Fx=@|!L{zvWQ<O1K|P#5#$RnH5GF%tCmnSwMAM"
    b"(XC9rT-C<V5-5|l;i#ZBAf+5$L)B}zbU#K$mgvlf9l8ndOo3+xJWn6FP&Q6~-nZerZ{z5BXCfNH=>oSrB^cc>5!b(0?=5gUReG=m"
    b"?J-fP4n6J^j0SGe<SqE!98PN!iqhf*dH92*fbVeCDrbjTzinXn6zgYu@YjDjpN-s;<BNHcMqjMDXIxV-z5cyKu5Nj_5Xmk*#^pEI"
    b"53fD3=ECbR-H(tb;^q}{x?ReBM6y*Yl%Dk)n2Fi<L6d5+%cEhG;oEeLFuCx?P@*Z@qA5y?S7Zs*jOr;9Cl66L*S%%0tHuR{8~sO+"
    b";8LJvlzh>5W-jI?=lPeyyi4Zz&Q!^k>~biZE^B2lZQeY9$U<6g4(z5EtNGz5a%$4@4Bwe*DQ^b}7?*|{b+z|O`L!!|;6VyI0BQ53"
    b"Ed(W(^Jt-VrCc1oO;6=CVj<M1U1_pgsc5a6(ESP4+>7*8wPD3X^y1-R;cg;*NuqiCUjJZqvQA5A=|lk&xAI9LPi1CBn5=^dKbU1C"
    b"_LB53=IsYsm04GEBth^GUTc42-7>a<G@r`+dqn#wR7Y4lSuRxTW#4lTPPsXx-!UhdZ~on|@i-dE#H}q{=Ab@n;C(i@5K$7oAz_Br"
    b"8@Gxm*e_3n6G|l9qk+WsX=IaaTLpQ>R=s?a|A;{<=<cFm-}-T|mTT|}Me*;Mr~L7GTwj;+8`B&(9}6^vjbyRakRmJYIS5NS9Vsan"
    b"Z_}Z1w5do1DEv44E(#yweTy$zx{X_*I}o%YByu^43&qW}`Ae61*mB@H|BbWRmvYiBciU2Ep-Y2>n|tYR2=7=O_q4ZpCo8GHL9cWX"
    b"qK0-mpA*6baAe_FGNt=(Bv<rvk}I-?Z`3ai?3O07L3HFxQH4A0BXV(MZ90i=b;YCrp9XdUz~pU^_modKnvuBmHZ+Qh*i%{w{w*7K"
    b"3Pv}&$71QVfE(3+av{!C%v#FPZH-fjZ>4OTv#HOUJ{gNm{q|NsbN>Br*<^q1erMY1HwO;txat=gF5YU83P+Wq;wF7Y&8yI@{9&r*"
    b"RfVYZ%gaz#tBHJ~{RgK&gve?04{$%fletZ)zWe0`Y`F!+GbXXqv2>3A!|8CVqcg{}J7Rh`ne!rQaD|r$z7OyBoxWer^}SvZa+|t0"
    b"mLU!RqqW?WiiwgbwNpSrNV*BO*an~=mK(M>pc;Ls?Yi8g@(4&I<A}u{wG{3OEjOvej{g(-%H0)TM_=iy$fB?8d^ST1*z@ey(N~E6"
    b"gnOo&MCWYBf>HLiIY92^P<CLKTAOmMHj(-C6Z;rRDP<9pG2CDjwi?XA*HBNdMVb+=&#5htru5_?PQk{tL_B)JdQj6U(NLIEfVLcv"
    b"AdS@ERyL6d6Hw8EBN$6KW`P8a8H#SS5joGEN6^5f<{$Z<Ip8K^9_`O$lQn34j>B#;{yp4KC`6VP3WzBnzDWXa*B8KzNJtv2XL|Iw"
    b"kc|o(w(o?!w9@Q9g*#+k?G$t1O?ay<lJa|Uo0<oI10T!mXV*>jZPFLO-qvqO<Q5G61QFQWB8cD2%><U&(27q<dn+r3Hco{lkL_#D"
    b"G*C6B#}v4$t;7uwW~Gw`wK&x<L1>Z65KXFu`t{@{7eUr6zo`d$EqNu%ZpbFUP$m?}IZ$>IcY_Kzxznx6HD#oSg1TMM_X5@k&cI6h"
    b"S@Zo@!M;`nN!e$ducPi=WlY4L+3JX_DiokI3_Zs4p)R_o;d~*XSZ+E6sfen%6lW_EB}<%My-WFIj%NBIcN^}jaewq&T(j@!Bm0ib"
    b"i1@>|*jyBU^J@R4ov5tMX$;bJZe>~w_Lvc_K7J)L5+>%!K%t&1%9u9eX><cxbL6&hpW%XXs`lg<88&Z$^7vuS|DLFP&S?=|qw;1<"
    b"wRwW{6-&DtX#ri<3jY~Fy2PJ0tS#=w(_+*5{NN#}$bZHmi5cBY)WZGroLf0@M8yb0AFD6XkI*kJ5_P&iJlU5{r{V%Ee97Y9Eg)5C"
    b"xoHR8AR0IsPrk;Z%!_J{4=<rBx7*==Elt;M#rUC0!QiDXH+An8VP64^>a`rm${pHRMszB5w^0rp$%fCuk3_<cN(eu)aEtKg{39ji"
    b"2Y;*QT72R$ZgA+RL&v67tRMxf@*VhsDd+;z!KPWY2y1r4GB&MJi>S<wn9ruo(IVz#M@&@~zKg;P%<XJ#SH7nwGrE9y_ls;gr*%pN"
    b"UcK@KA2k0Ny{rbC11BMUoAQkhxX@%qCp~ybF3(E2h{wYq5AEQ2oE4=4|Jgz*$A1>k2iCL#LPAJ_Y+8Z+AunUgSN1op+^nhrLae-~"
    b"m$U*(No!!Ay>G*n5tAeKp#f^`=x-?C9=l2jrj9fRVkYC4_WrI9lDS+KIjcgyI;>SgHlgHvd-?$4TDkOlUhU8jY&lkM`3gA?H?)v@"
    b"<!DPY*90+sUDBcZ&#Wf|j|ZN+;dviMQkSRC%gZz5<r(2e$isg*xfheSUoMcq{rGHw`<#VNLH;5magU#x$bIj87|b@?A$Kt9kr#Jv"
    b"CGKtD2p7SVysQp6x1CQwusi*BF!~gNOKqK-c|hmA`1@211g779suq5FYdBd^Nbe)*)^WYHJRqkHL$Xcy!s*eLF2xK-$q$;nV{_n_"
    b"TzgA&bBio(k~vH!j2EgFT8^{4F`i@kGoE9b(R0l7z+a__+;dC;d5)3axH(zm|J;xi{hu3?M*ru+s5NCdpPM{ho-F4qB3sX-<|We1"
    b"v9^?}iC7{P0SH6`RL&ClWRF=hkW3zL$ZD}_DtX`6no8amNJ+EDdeuQw$yy#Ap-Hv@{OIu*)bCNF$XWl0SLBY=>xuTUzLej6Y*9e@"
    b"Z$xI(%-HH%;%ot3h+?r3k?qrzjNN*lR06ko6Wqp8X>J^sp-zs2ZxehMae+lRppZ+3mr0b&a-y-W%X78k!MK_X2czh}g%lT8&y3wN"
    b"#vaHjoL_934h~JgQ4mF-gF@f=JWL%j&gIpm55NRbrMhRS(eK^7I1^oZyUJeqZAQ|272k|1f~k#@5VLlBl;cD)p#pI|3M8R1qL-%;"
    b"BEzNl%kYdVbGbdO&h!CI9NQcuOnjAf4$`zZ$4Jg))6lw`cCxuWooMc>ZB!~;&Y|=kW#OMj1+;k>E_#v?Z+E-0lVKCy<oXnJdEzig"
    b"t+`zldNl`L(BTE{Z!dB_2Gj==J;{-i61S7EympUkv`+$Lxf^L$l7m`$4oy+m6I}*CMghaX7FPly{rjhgHQ25UzD!p%E9Bp*y!Uc8"
    b"k&=;`y*wE&MNYV@d-YKB6(6c%@Y9lgm<}_vwz{2TBIRGUD_dSBax`Y_Qv5G#Hb}+@p!eR+=fmw^J0D7QoU^3Pi5VA}69=&EuV&`M"
    b"?HA66n4adt?PKSI;h)Y2y*c<k_V=Ax^Whk5^+h-z;6Rzf1|em&S2z6b)B&%~|B>ik>}hS!>I*&#BEt1fq6evZ16h;9(}sPkCc%ar"
    b";|0>yK-Dg2<-NdX#cMdoJ86)Y@IjKS_964bFQ^lP2H6RzTw338rdpeF=B2FB{_G|7uE;A`a!sr9qd#WNG^taaWmy?XD>!j681?Gp"
    b"OChUDBy`f6Xr;;RRM!L^7?sHgTS~?ZD!K5(g)rvecK{V@Q~u?ptl853(nV(roo^zSK^yR}MC8VFMn(Sg66ooZ@FC|^p*;7R)vPbR"
    b"#npQUKhOX}T`&Sg+T(Dpkp+HrjsfEN*67r_6eR#$>fE9k{gt{<QHhSvEzA)&5=7XobgP0PM4_2-IKt9zsrrk!k9@^3g-TSYw#Vgs"
    b"G7yOuC(_&GoSMou_~+sKLaWv-_LHN==-sfxzWFiVQ$(0~qgLvXvAh(=0{Xt)<D@KH+SVf78Ch|Sp;h_s7e+NzZsDrQa!zjxH#1e%"
    b"W=y-=T^;>`J)L%T^f%bgA*UAG+|k{IAIQIzCU<n#0)SkME%vmvDvi(5=8+UNq_bW5PrgO9DUZLHkv}`%+sPIfkIoe&2F(^=As$=W"
    b"-Y;JU<1s#KJW5B@K7UselYgp{`rIJT#uh*lwFN84lwbvReuazPT+Y!EfR+1WzLQsmx**vH+AfY<1z28a`=H!|7kQ8Wh}iCEb!s~p"
    b"&fS~bUW2mgBYt5KVZU31Bj)zBk8Xp|%d@Z!bXBVGIC;%IY)E-@Th_|D1#cB|Jj$lAfiTs^k4`lYO+z!EV%Xe4l%3@(V6+dZ*)W3R"
    b"iRe30-*uON<Qtp3{%A$q<8JFjt77TWl~9RZv|h&QxW{j)jK{p~ouK^i09Armoy0@LwV=#b<u(sO!z}>y7Y;>M$>M5a{xO!`K=mO3"
    b"wl?_^GHo(aZ{GX?*-rh2`Qf+lC0fDFPQfDRK7-r!hB>1~67_9L%P^6Vl7*@u-%9@xJ$j^p@+ciA-^LMJQT=+Q8g5jv6-&=5YcXIa"
    b"<1^R_lmg$y=V2>G#8xVtR9($tsP8nETai^184JUnC0g9AszI_GBv?}jFFkfdER5aCW$k*qI68}5GQpMJ$Awx)W&C<qR^aW}Ka%#y"
    b"c`vuXM{*kR-a9KQ@Z55$)~OUUmsN!)RNWVNffhPZ!KzcIbKv2YrL~4J79AJiBoy2nKn_v&S<G9m?8P4x7Vgi%H+*`R@}SH6bC#+>"
    b"$*KK~^umfTD6~un&BYhiE`(-B9>7u~%gQ1@d5m;7N<y+Fv`h@On{3e?DD`U_K)XLb@4L|-6KB4Cqa)-R3ElS<@yohCei1p_wkSJy"
    b"^4F}<l7scM53Q?w5oJi9Nk`mp_Yp!9dmcauQ`T<jPGEDo`v~sD+7IZ08}CGhA?#|fnL+RH#z|cDrky&ig#_|#(c8}Vzk+9jni{1_"
    b"cm@j>bUGFzS`S4R;cNFf%CUmE1(xgf>OuxK4&Fm9K~wJ`J67@j92`HS6{v(ZBCOS6U->s#(i{`B9gF<Y0;BbkZs>Yl_jTA%xtTRv"
    b"I<Y5=aT+hRA}}}Ra%DMI>VuhcV~BoOGg{md?1_7fq4h{yFKHyh7*bJp5>xv>6N85~Jk8!_n*ghn=J|hEmX<4Nl0|N;@Gnfug$@`C"
    b"J_1AZBj>j&pL4lkJJnY*aq^V;;l+GkxmD9o*@k^#Z?W8yV{a*0TgY^E)H#ci$yCfN+t_}%BA8)}z9a*)Gw}$9{#s!*A)9q5ovzvy"
    b"GIS4OWbCvMY0!&VZY0#pfatajRJB-Qr%g=SRTgR3g||LSxY&3iRGrZ47`n8^nbm!odT&ZE_KL$lQt=eNkWaq*d1KBac)A#kCyCL("
    b"(2$XUdf0?uXh@s>J~8sEGNiK(R~`3%Ru(&FjD2D<4%yGHo5%9(@vf=p#(H9#)2*D)Yiz@BVckM&1b@HCXQ%z_+5z^jBD>EL`9Yce"
    b"6eP{1q^l{ZNBLtWX+0%fE%*~+cRwXP1xfRJv5sVA+#+2&cq<pvu<)tKCRH5>O$yy7swc&0#6*ag82W)4L7RtvcY5J6i<HNGmKU?{"
    b"scXX=ID)(1$LQf(wy+Uod{muf7XRmEv9vMvsmXZGma^}cE&g+s4Ta2!9^aen`=ue4@CvabCO$_!i1npQaRajVn}d5tuO=3h(Peu!"
    b"UL9!`B2J-Shr<+dewFayo|Nv_<9B~OjbRSW*qFFneiKtig4q9|xx5S3jf2@L<w3N4*V-@ayQW5G#zKvzo;9$&h^(M$Z>WGZ3srD7"
    b"P8ZSjyE*b8PAuL9%5T3!r`FN})?(?oMU1SNEIx(VhKm1$<yRfxddjehnX?Q!&si4f9!-7zQL5pS8nL_t3T9?|AK70z9{B}sP-_=O"
    b"gyNoJdwiXRT?_HX6IFeoYoTIEQ^X_oH*;-)NfBXFMDVeFk$N$9M5yYc)n$w!W{Os$go$=M{mRzK=)_U3^=;JaB29WSxFhE|>Jjd="
    b"eb2guNXWCFlJi41qlKQ=l9Q|6vA=7+zfZ;L*-$c%&LQJaWX{CMgIGhmvi84|)1U}mVW??-)t*ou<dD2Ca<dpRC%+rHOJt|)$JcF)"
    b"n6yN@*8PC0GV>o*<q|A;?b56g?UJ=*?aQhF(M8M44_&GD2=qtK#7K!R(v;O77b5fO{-f&qdtiOBH>=*pds*yD6Lc6F=3ctL%r+37"
    b"L>`k)*iYUwwP!lhSDjSnnlTa5XN-o#*WDd4*&{!pdhJ>Ntw_mr_WkQjzC~~)SZv?F78k&BNZzQkkF1|>-*r!QB&hbr<j^u*xY!mA"
    b"49NN66{6k|7?6fTjY6_0(kS*f@?mZy0nMtDOf<e88nsn2rbYip{GZ&f<^SYn^M8Ie%K!P<*YSTeeWO=$G<_qvSa~p$nlsxpikr);"
    b"Lt?|w5mhwgJl8;Gr}ElQvlNK3w2f3%qew$o2rmr_z7Nm#a3^I%=BC|*i<c=?zoN}fB*Z9GFS2@*G?}?XlNhQu_1ANO%VHQ#Y*E}K"
    b"KoCi0)|(>rC2Sw07>(7=6Rr#%TWdte<h#!A-!SyA|A<4Ahw}VSkm7Iex&SFA*=(mvnXOYD$Eld{pLVI3F;Xej95ihqUO$zeLYVq)"
    b"xdd&pi5=ai)4KHyJ$%{#PK)?2nJ(va1RM!;-ssh<*Er4cR^~cKZk&R<rE$u(pWtxLRwcjAvoGYvIa(N%Ia!r_cnu#XLaPaW4<zf^"
    b"E;Kfz%9fk<5AHv-|L^+`7Veh67(U5{hVOv+NQUi(KQZoKJI)Sp>&3Nsc7VM{zuY#!602|Rv*<GZC=paGjxwa;8muDx?XwLeom8BK"
    b"umuP`uee=MT*)Kw$D)>Hg0jXzS>ion71VtytPJ=S;ny_$?(jkXySnVcxqlL&!@p1$sW(W49dO`94IRM&`4n2#Yl*A;5x2)XUbQHn"
    b"R(_aBr^&<tn*XyMA{H@|NzU^RxOI`K1N)HKkFs2;CP6PZu_oj~ReFn+x&+Gg^2sb0MV6afTqH2vBtq;j5?oVxqshbN0x`KX*~66("
    b"Svy%p;C2U2tbICpsfr0U>Z*peEqv(Xn&Ho4Um8^v6XOAt758^p0m}^baN>7~f2Yvwk5_b`CHn*rVBTDhQV-wd1`&4rKhU%R#Q6H8"
    b"m24VWLFmC4NMnzM1Zr!D!q;8)Y(bV?gqEC;Q)KfA0F5IgsFI1b@5MgNVf{|TMTvffjF<7sA9s$q;b&_d;dsy<*ygtH@~o3C5Z>1W"
    b"_x-h3r{(ruRBgujh&QiV|DaBqw?vw>M82vGRdbKx#*`N-ujZ~L+q|bP5|+9kO!?W5GrQ#z@VbU?m#fLZ>Xr-7pRD?J{KNW&S6wYc"
    b"gsVwdH}I}h=dVdiH496z{_+g0`1mDK{t|hjSLgjASpa`eCDBlIrgr^8HTJYx!&8rBYWU?NUsuEI{chcii)?mFw?MVFpw9{;)5Vo1"
    b"Ml<exBulbC8y|1evVkLaezsU%q&6D+)L<MQo$t%yW9GZt)S5lte;4Olp)s<w#-xhEp63IU>VHA4BTKiKRORFI=?U0Wj*nUFBkQ_Y"
    b"KaR&7J|6uz9?NumKvE4?!Q#5rqg;V&s2!(fs^Mw~s`4laepi6AO*t|~cXkLjci6~F75^3#%v0{%k~tb*PkWSQ=}`(zT)BA*4Nbl}"
    b"G<er+XGdM`|9EG^SFG_Xr?MQ^<uVfk)b%)OtnQzAV&<;G<8I|mPEG;L_MPvUV9U(-fztf(%}S?-({Q@{h6)t3{3Wikinb_PG0fS9"
    b"lr^;ZXE2FqZqQ&7QgI9X7|@2K!K6p~hB-w#ov336xJOO4r~5;l3GY#O2i%k=PxHO1PnL1ZDsY=TjghkGd)1gU`d&43e}satk{Pac"
    b"C<9|6k<=t+Y0#zmEtI*S%N|hVFGBVDAdXJ5R3EQbAFpMf0e&p0K0W+YAQwy2VSTAuMyeKarKnm0Rm-4O%gC!`!fJ^G4nY(HDKN%>"
    b"F-FW%&`I!W$@oJR-7NOF|D)-~KERn{kK6iQM7hVRKA0@FKKR)K7gX%_10TiC<uKDT!vn$n=v#SpyvcvgxS>2EJcCw$EKUBX00CVm"
    b"vP_n!ujlC(u$UVQ#5<?4&vVgIt9DURDDl7%W_m7C`<w?x`!JU|U4HL02!JzvBAev#>RXkB8t(sG2&OiClC_3h<S?w=9qCNtHi@R7"
    b"8re<{7QX`vH1=r}Sg6L%$Em@*2DDREjj%Vc4j%<eo|9%YwznyJxor!TgjnuuqxFLb&c38TR&aKu*&9^pnY%)!=ctdyy@-rYsB_ip"
    b"w&=-UqkX16)xMiLpWRiv$oU1U4$X(lrEsHsYPCjRuth`qP`v=CTwMKz16wvb{4u~!wf<IV25?>@CIMaCj%{>9|H1}9;)K}AC~p8Q"
    b"d?O8wd>L6Wwm#dTD(r&_Dt*_1Ppg#Sx7kGY#>_qbgh2FwT?hWoUMoC+c*uc|Nxskh)e?xQkl)5W-H!O?iy}4f=h&0>lU){4%8XU@"
    b"Gr<rN3X+9nLsvl2PTg|<pm5)z^AEm^JO*My<+f;Bdk3p8U@ikYI19;9Okwr8=)VSev3j_uZi3~IOkc0lxnoBxxZln1KBJG4h3yi&"
    b"zRUBF6=6%clwIdkDH3zAoclqtv?@>WK%#mM=IKe7ja0H=ntcc2m`6lADG=D|RQ_;Q9dt>51Kx7ii)>fb>-KjxOy-%nd1kg0&kpT="
    b"*bi=U;x!zN%#n3emts+EuRs!atI~>vG*clQQFftYLJ#UHFIJ1ak|$8JP2ORj-nEGME6U#x7ST|IM+5YhZlpH&TAd-dCo3t8USEP%"
    b"EJfoG=geG&0XLhBCvhCH4$z0`^d?s;rFez6&=!Rp`AXb_llj0WY?Ed9{i(;g|AyHYo+>=yPdnsNh8la=(LWGE#e68s;{J4njPjq="
    b"p{ul@%>3@W+p!omv&+wobpf7<@8R)ZoxL#Lf0Wz^L7g+~V-y_Se~IRhu3T07eweSs|6%$^E=YgZMba;|asg@+bEzuWkq!Dpqpmub"
    b"V*ML0VTZ}DT&{Wh?#0QR7pu{@vFKQSldRx04yF=1U01np(Soi?VQ0F<_vJ#_l+abH@6s3NbiNI`tKi;PFK}*YmR<>Z7S~LXsaho$"
    b"%7b%#-#Mi3>&7keNBp`KSwVs!rdDWeG3mD-HL+Jv$9t)DPRJ>Agjz&p`Ydi~I0B2uyaNYru^75hFmG?LUL7*1jx)>1j$(u6e3gxi"
    b"QFI9{Hm!!eEThD$$-=*c)1`wg&qWGxj9nK~(3>Kx<5_7mIX}pD;el&LjzAh!KHz!>;gT46Mpp}y^@{DdzLS^Q4%rXL6YXbcvn>g&"
    b"6hdVkp_L-1p**9n<>m}wj~*<IeN<Sur*LoV)575x79MI5LN)TG%wpWlzBCTRKA&EAx;sIK{2QTr1r^959WFezrXzH>$UE0-Q10u>"
    b"^7pk(KsCtJ<y`011RrF9$g78=VBhDQw`GE>KU^j(+<&3h08uY|&K=ky9rZMBtedUns113%3K<a(J%~FdVi>k4ngAkt`^jIoDVJQ%"
    b"@5&?H=kQ*?4gYK~umoLg;ix$m*RqvF%xUA4<eSRr2OzK}M=n%8ctF!`^1qh$v?*^~rrH>PMMM_3GM(3o%fNNNf=!EWXz=P>ZHmC7"
    b";C%Z+L;e1Wc(;O!fB5}ns5UZ1*_bIn!v~cgJ%D&1Wgq?Q!t7O%EcNRG{@XW^|MtU8Ucd4`=D&UU$NvfcZN;|#&-}M<YW%k!s{A+Q"
    b">-cYmHf7hL3;1t_|DXA9WUyR!`2Pa`t%tLdJ*@6Mj_NPZ@R9is@y}4Tr9TH@soQ5~xUT$%WK52zOy^|)!eI^Ea5oB(j7KZW?l$EK"
    b"ZV&-35(3#>CfSRP<GH+rvXRG<cZ!rbP){lr=D<R-Q;a$KPwPpVCR^47)wAB_yXR?xIe59AJD$nNnxx@Ssv9GF)W)VEQHTgdp7a3{"
    b"KIXzC?aE6((d0LX(LYB1sNJc`A9+Z^YMCm$VbwBjb!M_e2KZdJ^1YvAOM{TK0oQqlTEH1JnwdNUk0Ph?#N$~~91lO9CCV9BZB@_F"
    b"q@CQJcG674es6=7_)QM&QC2>lEtOI=Bp1-!qAyz%I`-$$7V9~G)Oe8tB_ki=2@Y`i5bksV2}4{&WQc5h=2a#3kD!zY>l^E@YBQ~;"
    b"GFVS+8rBS^)<vgODW7gQtu|}Z>avSWE0Rk}(3ILdI;Co8O5JIl?`~JFc%S3nIHe#2y2%ktZ$#Q%t;eYp@>m!F2OHtF8!^b`<nCpK"
    b"746~A@wnXWn!FO>F(~*j#0}&(K!+Vd84h@AH1P-2y$Pnx!83^G4a-HD?&VkzYzrCUHiewS5Mx#dq9d+0?kE(6;I(jQ)lGgl5De?a"
    b"!iSeyr@#>~1u%_E!cKi)K$;X@rVE!X+PhX*wCA3G4YwFzd;+`WkH#c}Zn#y;PJi+2X7KE$V1I<m!ue{BlQKDeFec@gma;mO;o#CU"
    b"-uyP$U~wU38WUMDSJ$e1_s7}_Xh1rGCahZ)Z^z|Z%f;SsfB6@vf&+%67Bh6U@(ghqEr|%%IF*^1d}@e;r2^wB(sDqX$~6$tfCKBs"
    b"?B}<;aD}`_GC@g!w9p{lr7ZX<NpaPZ6j$X>v(^h?t>@We$1@bhJMh2pc(3y)lPWScG|hp>Akco!9N2=Uh~0Wt)YXatqk#eQqfw^x"
    b"qFHNuOdjV{>J8jw@V(>>SYEH%*qPev<L-gSE1$nX?75X0i{QayQbt<ID=5<+p^B<Gm;=-Fn!34~hdd3SPH*8*J{4*>qm)jSVFy{F"
    b"s-Jk3Wy)OrXiNC1XV;knZ*j*9fdno#x_rA7<4?F%d=$@^!1|d}fLm&4QWFDgCAeGuJR+d%oDPtb7k{i>mU5`3*n4VQzmvgl>*2n$"
    b"WmK?gIiV?8$S>M_L95+oMy+-azkl-SsmBt65w2=R{qUPJm3CM{2XXgPzWr#{PKka*Gb~HQK5mJJYM&dt7i}mXlRploHW-EvM@%o^"
    b"l@(B*{7ilKg=(MaZ+M27B~*2?)Nww4fGm}J$aP#Ru|3g75VZR^S?xx?auLf73pKTM(u_b<n#P(0xJg6syDY&IS0!R2hT(%qreLMi"
    b"MTx3D2%>-t%o+$;ee3YSF*`KQMbWk!_F-&noK12E2ihXdf>gjP^)MpA0XY>BBHYIM=MQDfBC^9|A^qn+;8Q&hDnH5T?-!K97~pTY"
    b"G_t&wgDlR?Y!I^4y8`w*G|+KZ=WhrfQNn-bnW7cDJe9uVRstD=bd%l6uu(Pq_c~v+Dpc<ll-^tLY75#~NB=^sXbTCG!cq6My1W-)"
    b"2vUw%=@xPZjnEbFv?{%jqE}7eRM!1iwbPCvI`ZL+2T@x)kv?sQY{xp-wAWXlvgX`<xM!#3JX}|JacCA`+qtR@8Z(U?@L3`^!|~zr"
    b"UX4KoYLLfNIMnL3VbC!7i?b9CMVc*6?|cmUYq^@Rq!1D=z@YtVkf#h2UV}l~wS*q;wfOzp(Tpmb-q{%RA6iCM%%}>3dbErxF{3#c"
    b"B#$PX<MhtOpnuU4R%60>7<99ia6Try5`$_-6P7!@)fjYzmaqmBHek?1EnzJtY{VerXhMh6+k`<wQ`LkGn6Mdx-dBS>Ets$cgZ50#"
    b"BwXtBF2SHbY6+c~@J0-JT1&VB6W)YDkBlZ<>GUqepp9C>RhV!Y27OmccsnLsjzKF&6W-zU-i$$wTEb3DSc5@VYYFefgbOif`e?$t"
    b"o!&(lWYQ8!n9z<vr>Ce1@5O|*81%`MOu{aww+@32s8A0h+Y8fPhoLX4p+5^yXsh>n4E<#$`Gd%ra(W%qel3U1Y7X@n`XeoeEou&n"
    b"G4$J`IXp@^+(6^6<?xuALnVeT)N*)2&EX0RojIDrla#~sb_gxfa(G(Jp#npPCu`HVUG?uH77nq*>NOYABUJmA<^cM6f}PK)?7>ZF"
    b"xk#&gJHES3bn5;d-<vG7nE#7lh>5TKJHeC@%tH@xcP;?pCy)vPSx+Eb1pB*`O(nssA(%M?(?&4W1k+3~^9jaIFy#buCBf7X%uIr*"
    b"C74MB;~<zqf@vU_bOd2q2<9ZdFJDS9pW?gQNic^9W(C2#K`<)`CQdM`2<DFjb34KOnqclAm|qY~C&Bz1!Q4qO4-(AX1oI<;kqG84"
    b"g1MJqzC|!y1mnT?pZfTg+^V$T=L6~v?Nk=x=R-aG)1}NN;LRHFR07_j0h<W;Q4RR)W(0mr1O5y@A9z9o{s2E8dQt=4N5D^Oz%c^e"
    b"ssaCg^Tp)R(7y(nMkIkEr+22ui>h&CL`TzdS2`#0Ns4OZFhyqpjIu%vTVXB1DSn9urmbU=I&CG98~PLD-Xi7Q2f2|SJZ-wSa>*c5"
    b"aJN*P(6u0U!U6B4@SZd$be&p&0Pl!zmJqeCutyBvs7Fhc@~MRGds#r=`$s_Q9PlI@dZf3Nv??#K48Ag!2;S?&`?wp<uarIB!4~X+"
    b"Pmeip4((Jwig(y?D9+w7k=vjc>3j^s%ox_n!wN?_pTIB+hFzzH^<tP)`Cps`Z9gM5vLejRrBpGLrF@JZtF1~od=fB?(Kues&@_Y%"
    b"O?!;~QY>PqfUFdWO8|S(*X@H7TAJ%r-VbAL7>HQLV#s1Ih7@TbF0oa4G0brg3hbqv^*l{46|h*1Vx?G8$R!SLN8I&MYC#ue_n3w@"
    b"e2>a|LaY7i@IR=p*Pwh9%&Lf1A~V?I94~;@bg-f)$0KY<NK~E+X0-(B)JxzFAq(DX=qXd!m~87sHQ&Wz7GO^qrABM%fX;`D`*Z$!"
    b"iRw1F6s<sx<&OzrJ)n&fYOA{}wF@_y=2Z9S>oG_^7O%C-U$7WA<>^ErEBR#duVd+1OF6z~4xle_Z#7JUcYc2{ge{(pu;m(5gl$@A"
    b"48lfD5kup&MhU3R&j-gPhTLNBlQ<}$1sKBhgNmNihGw8g#ps??F*=@`B~*G4CJSp3LPhW4i<9RPDm{XDVSf%nA%yaSvH9KKqau7y"
    b"W+QyW?{(W!uvA__Ebow<i&9;;#yyc6Ozlo@DK3L+C-BYTCRi~pZwUrj)u6VL!jV?*L<}mPpe~lk4P{R6Bn&z?o<n`Nyl|x5TZTbN"
    b"^q;Vd1G<!Ds%`zYidL@^qhB4L$;9gPx-jTPHIthvA%%B}8+NPzQiIyAz|tpU(7%l)obB|kz#yNNunH5Rdlcn+TEaP)(2YUg7)?0W"
    b"=|yMCO0$-59wuzXp!qz=AHTA2q|MugK{K?3tpBzQ$5cJPrCV8(sZMN%Rqb*rc@K^r)n^_UJ*q!{VDzZ|7~h-93FhqwM$hWK4~(AG"
    b"J07@T%U9{I72L4DEp0nw-)Ro4f%&*_E|Oa08MbIAzI62d8P{>4vt8*dR{dU^gTv^E$pFxb@qWIm451kY9yHX=gARsPSxd;FgYv!_"
    b"G{PZX=b!ddNZ~ODeur22_sxM{;_q2=;1~D{)%h7}f=7FV8V6~GcAa9SSS9X4P^03Q19$6H*GwY@^Ml{gBd;TkbY%TgNG#r16K=3x"
    b"3M;!B(#;GP2L`0eY*DT~8m>><`!*HX1`<MzE?n%e_ia2GuGjlx23YogX^*Tnw70jB)&-txBV?7l9E&{5MT{*Sp?PeNE!q*nG-@qR"
    b"XeyDBPD48-MqSe?@<@Z8dIM2aEViQ`{U%@?(L!{KT1`hpf@+R~lk94!CO7@ll(xq<O(v=2rHc)=0Zi!&Pjo<`Q033VO?rO<tGo+s"
    b"-}F9B+b<HogVE63zre4Q?^OO2pg!;2N|(W>x%vl$|0fT}N_(EdNM%caPHH~a{DCoQ?G>mJR7ON(i(Bak5IKj>#9IO?9n=|6HL98e"
    b"qq~}xd>gtodkQP}6xNI?>r|#;Mnzk-J!c$G7@A8>nY)#CGA#$1zoU}+8T;REThyukW9_DSEE+ZxM5VmN=3fie<Vhxr;avDGXfi(~"
    b"Sl6A5G$9Rt^=?%SIir7Wi$+Wn?R(Y=_Se^OQ4t*H)uDom*psI#FB|7(c}|z|r?g6jkR~&?5CIe%B_y8Cgc{RLBD+~o<6Nyu=)5SA"
    b"xy4A6h*959pJ)D-+w1hOYId){UN@#f)sgwv#|Ebt9%n5gdpmTu5c~V|{T~+YSrcjzSI0B(P7yYIc7mObeKLLjVBzZ__!48E!u$Te"
    b"7rwD3<P<}qW=~7x_E*r_k?okrzH`TNhfWuo7y7;s`o4J2-6+>gDu4+$98D;s=@iHqk%NpDDBnn{<|bVHg&5{;<pAfUyOl){Y~DUW"
    b"Wt)@F>pKC}bfW=X<$s?e$vn6=h&P}HNu~VQ!taan9JtAJ_YWcOa93>55?U^@acqC=@0QpROW{7&B*s3p*ms89LTH@y7x;V$8G6CE"
    b"Jkd?^B3uHjyC1iMU|jlpM`&Y#W>w?@e(vos<?n2Ry0x^saa;1(qPCQ6fSrbq`I;YAv>u2AJb0>+Re@wt^h1tSR^50z*kGv3S`l8R"
    b"Lyu%;^hj3VJ6(W|(u!nbWAYR3ua;z1&{UUyq_Ag|wafhAQh_{~>*m+%d}preGW*Uf+*Ckx<v}zjyoijy%LUue`pn>TfqTAIs-(;P"
    b"ib1mY6{9(5B(uYV20>N%MDNMiC4)o8>=4Z0uo3-<Uxo7NV~W~o%qj}WS%c3TRVUkT`bQR-AN++86{*5oTA-e3>rbjLQr&Lj`PIFf"
    b"N~@Mk+fWpReLlFxNHtw)<aSFJ7SUEc73M&fS5S?iDP$)@<o#6&{nf>dhw-gjwVN+p<v%xh-DKRpe97vjo-*iDH09NWvNw&%|3Zpp"
    b"R*<DJ`EO(a97l4|L9LBw&M~WvXp<4!_!w_v0DgigtS3Cx@+7o`HXbs)u@T-dW9bAA{zV%x^MBNc%drt<qm6K=Uac*-7&MD+UCE#G"
    b"I%3_ao)gr1D!iV5fuC(iLmWhY&9ZHU_<Bk^WU%h`*v5%tsu$SKd8iX%_IGiPX_mP;teS;-Xc;wNkQ@T>A>;vgL`OE9!<ht=UYi9d"
    b"c{unZy*5S70X&sqnwkSQ(Tg#OJ%>8zay~W=r^YbkVcv|aN65qca1EA3`PeAvsxf&_*Pl0^%m|Kz<-r_1O{qDyv^pMWOAi{Hv9b5a"
    b"%e=`Hei0jc*yzj5+xJF<9g(j3ecfqiiB7l4tPKJm$)|R>AQakMc@blGSE?n9S36X-cDI)2Juch`Il&-c`N=4Xh9QfQTEe?I*}wu;"
    b"qznMG4Z1M0Aq~BV9V|`5#h$OWI$6FgkFRMf8IdcZ&txvo%0E(I4*v8Eo#pp(+diQy%z^*H3&^>$du9T@@!i^-uH17`sLXdY&4HHs"
    b"?Pc8Hj3p^*fx(pd0c2UA{0v-v#=-CMdU%sk<n?ZawE<l}x4NCm^QX0q91b>QE^jalA0(lD7!qS&aJQUi3|Ipk1FFW)s(=+~B6Zly"
    b"W+IQEM{_;rH+JEI!3j&#lh{GB*|r<D<^fxZJTWF~Ah;%&mP&1@Z796*CzLO-?dE1xr$S^cM2@CWH{VsTPj^|Rj*uC0o?jRXtv7@`"
    b"xgDYA0&d#h|H|$0x@VH<^aeB#TT65OP88VPY(@GGHW`f+%O+}w6RL{3+^EFx4QToxo`G7C#LSpCuU_{Pc;1I+>Xr4n7(5%R>viwJ"
    b"bNyBIx?*^~56`-*>vdPcv#y#yB>?xY)%^J$gzL~{wIS!ie@0`@*ZvcPEn1#q^1Hxdr)Id*@bzA=jmH1$`Hek~(ayk}XI||=&(#gq"
    b"9C&i!$%6-Nx8}oB08b%Verd24u~-|)E4IT*hFRe52u3}L2J0nf;Lr5yH8W3A0eTHdG#ln7(Vk)p`!ccEfa>%$FeB!7z<jg>2V@hv"
    b"wd@E@9}Geo)PUJ!4x$af?k`EYsy|P!laYIN4cWVK$n#jymf?C`q*(~vEOfBaM~AsLk8sgX;Vsc@%<XB(9YtWFYEm`j6_qQYC~I#I"
    b"ruGP-W=LJMnWxFYYsHO%mWY?F!uzt}0~dwwy*C@Ci)wVE@Z?6VLW{F1#QNCrm{JD&R9d|}#Xf`fFSX8wW9_nt&;%E`OTGFCx|E+E"
    b"wH@k!Z+N>qGXEJg|A^?B68oEAR3ZZWAB`OmBG2cVj{W&)?3~5C<MrWp0HwVtpG1W_y1T5i)7P(^5aC{9Dx9t+<t|bgLo2-v9ieNt"
    b">ZQ5tPOHPb<1ORg?a5767zr4$3aGX|(JWLansanxt`rFDKU=yn=jBqqYs|(9&gRW|2@i$t&(2*>lBN|-<@a3B>Lz(8nA$L9_%Pp{"
    b"HzHZH!lk^zW0%WAk@Z4kgFcvMhc|vpbsUT~8xYN#k1|1s`n5tIIh5OZ8lHXI7aI0UP$(~Xl8c{G^n8d8FSTBY7WQM+FgL4oJ%u;i"
    b"EdM-wL;9whY8P}}Wk0;O*k@lTiwR@(P4>g<PQrs4N-Z~Zq;=uKbFrSnWOKL>L+ITO3C8*C)p8C(r{I}|af#gO4&**39ME$P=sCyv"
    b"y#_$D53cbgjjPSu5A>`w-j-;v2zZeeMz2|8^da2Y3K8fwAWM~F#TFqPo8=?_2e=I79N&kVl7;XAmk7Dkx7&y2DtZcL>7wa$4nnMs"
    b"E5BT$*&Dt<BhXccGI&U8UR%;Vi0^apPf$<c>yB3KVy^`C>_a9phv1CAO7=_J$PmxOEG4+$P1N^9HJq$m`v{pYMb0r^Sv$;sxV9sh"
    b"lA4|s*juVw<S>~py(HYMM<ZP~YD)s8w>}XIhwO)?req<a5@{4QmI@({_4;PWMgB7s;D!Qt61p<m51W4yZJF7x7GLv7<|<9!mHa!>"
    b"oIX$aMD6eHqj*lXwUgOOw|%F_97Jhg_Joz}DE-EY3;-`q>#|NC$pExR03p#d@RX5pT*#mVYL_u+`9pby+wE>^SKb|smFnG!{q9i<"
    b"hgYMWsJ3?P(xdz?3ly$amb>X3+^SJBLwb3pW()5l2=pk+rLo>UupM!?$ElpUh0ud?LJzocG>=jtWsw+EU?ejA6kGWyHP#6T(UYnb"
    b"iT1_lQzuCVh0$!~TJ~ovGCQ_oOd^jXyWvahJ5i)><0PC3UV-CxF6GhZIBJHNxaDG)_@r>&vjwR^L)@P*%&G1^hqSn!ysrNqQ@f0G"
    b"Wk7SHivAJZZETsPaJM-yh!vMbw!sw1aUf0OUQs76|6~1g-}plX(j_h{_-i;%no$syrZqL!e6=>W=Dqa>!zVQ(@OBX15;d>LMN8zj"
    b"ZM$n;F$d6c?2CxsneRvT(C|BhA@~_e=b&_@zYgU!b(;jQE;)H9U4&um9q$C?riWl{2{eA_OT%^u%FQi|hNnw23lB-to0?tDHYN2Z"
    b"RTM-y`X?HLThQ9i68TNrZhKtHr&8A%hTmCP7?tzY+>_%df8_rm*=R3|-MV_s?y=U~UVT;5P1msFVq4TJhVz`tgx~W4P_0|rc8ARw"
    b"%htx`<QukVIIkHk#?NJ+p|`;*IS*l)*>T&UQRz=WviCg8GcxgvGU&A>BK!xXh^%Vb$BrlW_|MK|ahc>kM){`xqgJwE)b8$Jiwm%-"
    b"wYFnOia_J59qi@;_?^R!b7aCcG>g<8KEZvfqb|KEQm%*iY9x80i6pbX!Jr`u{)O~<=IjphgY)?7j_cQ3LS8ZC6+*N5?rV*A*mufS"
    b"wphI3S7h%QGLcIcdIj0CaJFpf2zd)e0bi3VS#vhv<b`($a>>Fg<qL8}k#wjSk|;{Zwm%8OABzb28$CqP>lY*Qk?vxR-0~IRrqK>I"
    b"se|R3f47enwzayH)KQHjg;sM*;K0FC4_1Qza|7N)t@0l1DHUI`khd<bu3L`u&t*s!3LZmp(57H_+z{32UM7qwcnB-L@yZ}{ntTQN"
    b"A!=1-ALGiHC=P~qpd5AE#0xKANbKOI{kGj5_IEZd?~Y>>yl$9p-Vq-@XgtV<FuxRBFZ7a-hJ!UiVyt<`)WiF4V`>QTFrQ;mjt`D+"
    b"{SF$$g|Jbs$78h;wsO6$PUi!hZXqn{g$>r(@*Ma(5Ah$l91)hQ(`opahdAN?%ii0^M_FBo<MZ+)c}QlMiB2F&z)_>3L5&6!m_#Rm"
    b"3E?F$lQ0tz2%s>ADFTKWKutp85Y3b8DBJ4RcI&Pwwzb=SSGKw?zEtyqNkA(J+8PVBfztMgp&B$M0b=HN&biOL5~zOK{q6oy^k$y>"
    b"e(t&Fo_p@wIpCSspX!D>Z|zTpzc=+`{Wm}_2X|FYbq{|$WeCKqtG|?z>)KVd&|#HgxF-Qsqz1|@q3+@Al#itXjkE|B9d}218w*$i"
    b"gobzIfot(HZh%sh1kw8CajPz)?5!?51N&?(@aFrgli$i-T%a2M82lu!titPGz63YwnuG*PSi8StxxY85WlRg5JSQMn-F3N-scHkl"
    b"W0hCZww{h}>lyjB9(L_S?D>g+VI6Rc1Ke;U%qTCzq!rmnYwC2;MY!pn6uC<Z2FcH#U#5^g|6l@!K<urJQP=z<^F23Dse>V9l%JH8"
    b"BP^p6uOjVV$W_^NB)p(}RjAJ7tK_>}io!z6r-pjGJLl2KAMmUd>5wy+*40bqNesKU!bohwFs9!Ge{+I#jUAfL>j;1_)~j*P$twrX"
    b"UL(}voft4J44A$h5cZHC;(mdrGFLS<!;huIds$YCG|RLQ^I8MC+Lq%QNuLhhew~zu!BSp2ouxhpe?8WU44k#(KY=jX^gNwe>L75d"
    b"6ZgKm(N?@(32o26Q_0j`a3{)YE81$S(Qxwfq+{s-RzBvP#fI72jmE}9b0_&Sb|3Vb8trQExYWLh{$>rH1swGC<}~*wOlkJ_1aYR_"
    b"fM*!;E3kxRUnvhv1a4uapdxHxMM}f+4ZCsmtt9j4qF%+EjeZp)Z*0Il`{(!xtVio~$dgO(?3O~_)?#A{v???haHCHoeB0<MsLm;W"
    b"d?pwKoTKm~)CP3TEyo2(k7&l!Sza+WyDBMn&MvL3|5IrFT;IJmr~L1@vp|Ue<Dr~&k!;yjI>;h6+SIn(?CL?vmj(GM!}%bSw)27+"
    b"@N)6+M?Bi_rVUM~V?TP$EDiex8dxIV2J8Az|AA1=`-k^kyPEre2JMf9lmJGQwzz=u_diM;Pe*5UQ&b_lS1>*vQ!c_rWZ)*Oo0Qom"
    b"kb+y1xAjQ>tk7g>@#!oyEclrjG!I7~NFJ+j!RpW32VRxW#nRqDVm}BAz&D*F=>Q*fkpDHLN0zo9ejH5yayYhxKMe9fvLl!<?G-0p"
    b"<<leampJSmb^k)9r&5nVB$Y}TO342jFAhsp3Zh^v1F9`i%At$Kq&i!!r;8CY0OVB!a%odVsB8~>keCf%uBT?$A-@~Gn$|`dQ$k5{"
    b"4q_JlJp^l7In`kYL^(?A{nae3B7_A`BqP&Pq0J@kCU>aHd&14JJJ?baOpi@iRtbN(1`<||^5Q_l6?uB_j0alr7WL%}<}$^^CwP)e"
    b"@F9u(Z%TaH&+)Rw8`z0UGb~-z>6SxPnU>C7X3L?PD=nSXQ$wcOES*(rEQfZjv~<=?upFvZNT5(;H3GX08IFJ)JM{4={jDV?rnMaM"
    b"UBc4#EyNaES`E*(uold#Z^n=#mKMVgTFD^5n%F18c>bg49QTi?VWmM!j5dF-7H4xGn*T8ea_i~A?qiQH0X~<CFH!@!0UmS!f&!+a"
    b"fg*Ka8w~CDS(moEWlR$g9trGDyygeN;G4KL`Mu#WAY^*G!DP#CstqlF)Mm+9pJ+b~EV=$ne@fV^{S~U-xAN=DAW6Tq2dhkEZ*{`2"
    b"<#5fl{=TICD~H;&K0SiLbOC}Xg%;|%rx6<MlFS)+31977Kxz|V*)Hj^16U`po2*W0>I=k68c9~*Vdz_unH$Duz|<lUE<;*nm15qA"
    b"6mxz7X~_7st+53OEx=E(5317=f-A30kf!4Br4TARPqpgWgsS8lF-{5PNfeQ_>0PIye)3(^)CfqKrO==%S`FxwaA4X8%Cn%OVf~+2"
    b"1in<764Lz{dCXIyXrJWjKVReOKQr;+Kv-QY3KL|T6{{$9@(RcXAAhXll1J8smyn^bvQR<*aS5Z>I6iubW4C*P_=G%4Z{>_Kd6GN&"
    b"1r5H(AqAB@ts|1wXDpLH*%19mr%e9shUmOaT_JpZa2~$W-tCRn$~!q4k%rx$gz?qo<d0S^jxV*L{@~Zb*SoO_mjk9dOXRoLhHr|8"
    b"^f0?ZY4Jq@)~u+ky%9x6Zk)gsql*?*8sF@af4e?L12TWBH3Qg|lDs5J<+ITx|7?9U`dsqA#AFY>4>qQB;x#?r1l*4pKHh3nl@1>#"
    b"tvn*Cz|r!r<J$M*)Z4uKHT4($XxDj<3ZwO^EB4lP;pc^4?z)%~quBQ&-1-t88ss$BbA7PM^?&gtDo;E>DqKl(r=suZ_WHjV9{s7B"
    b"ubJF+bAl?vV~^vRM=C6B8ceg@%rWM!KVsO8bC%WecI8n;T`OOd`tCw$y#6oSbxxPOS$S<Ib86sfdsWUdrz=+1tzq{Kyh0;P-u2V4"
    b"wk5NJXc7@kgcK>7^+1Rx1-$g;9gFb<OJlVW)9%ZVHx+kHaHBd<7<$M80UhCIqxiJ4o*v16x$W+-Dko!Dl~Vu}V&lUgPc(>+sX`$7"
    b"b_Gn?mS69fmUE=OxhA!7i3x<y2HhQAeL<n6tLig<o5u2G<&Q&pVnc6EFC~Qy@`V2miAC6`<)KEA-eSe-MvRhW)a0eqo1~yZ_AQQ5"
    b"Ar-BqH++ACwX*l>4|=E4>$yabh8Ow<!LL_d&$V`sSWzQby#6sKJH>3M0D={XXgG+aI)Wv_>Q+I;M0?O-!mq!YUJR#CA16J~Vzm(l"
    b"U&?;1RaFbXx9U`=_b{#Z1oWY3>Gs{h(oW*{R>ATc-z_XnCXWc7OqO<vJUZ}9#=WJbqk+Ovs7a7+r!fqL&C#p=kgvj01o&k|0u*@*"
    b"(~Ib_iy#<4DLRVLLCj=;pB0S;wvM`DO5t`Q*6h~+kQAWYcR5|=F$W5TkhM+4&ZeqI&R0oRT}NUzEXg`lBL3xeW95cfkuAkkc39q7"
    b"4wSjfC~qyN!5)M`S!42U^cdyxS&F6z@5G9Mg&LS!<&}w)s2SuiyT8TA@<C?qSOb!&QO*vho)$`dBdVl>l*}QN$j?DCq`@|l;dt2N"
    b"p|Gg_V5jA4@KLZ$RC{%ZO?lGod`Gr$v^=f@QGZS;`^Z%mcz9H*9_>h?=4!FIY#v(F*u{!WIYadaYp!KhBg@?fZ8k!iPbT2H>&@FZ"
    b"+nQ%Av}`q1{f<?S!Z)zHA^~z-!$g+*pGt<8C_^ARgHZJ`X4r;9JUy_~DBrmn8uOk!do`-qzlSH4ll3aq@b9MtuRhn2gq?!7UjMkd"
    b"ErwoMu}&%icDTA#RE<af%&B7-FD1vPpm-zXcLDK%bnG(uTa6|1)A-t;*o20y)S)m3ztoyn`_Ip)s&oM7KHz15Pb1zO#h;6mXB($H"
    b"wMN-zuEE0Y9jCBy%PWyb)G>vXDEdx?oP&8*y;f!TH;|2?=cZTOsv&&dh3PTfljEiH^+eY=UVRPm^(_dM18h{O>?#k|^r=dz>6-IW"
    b"_&$zpSTw!*L|`H5iXoRmlfT($m;VsHPkf`rW~`bH06-LUqywT$?DBW;Iz$rP9M!=%awz&@g*8--DGGl`7CKe<e%tAegb$qj#xE;O"
    b"2cCh}>~Tp2<yNSi`6_#b8UD&gQfTP;516R<?<g&5j^(hNzM#~-SSXYeC^9-KdY6ZbIVTWG{0E@Nmxap+k3!5}EV_UnJOHv%O*%_0"
    b"D`m<4R)IYzuoYs~Ic>*M-={0rgzPGZ>J!;5C|Y4rZO~z5Il<EUX1WC6y^lGKz<;wo4Cs<d9N7Or2HFuwWf}1<g4*V+5NZr8H6W07"
    b"oq24grvD~jKmVB>Vn4<Z`}q%g&Pf6c07<-R%1X#$sW$q)2L(ppip2*%umZtvB|uk%7VZwd&NZ6SArS<s*lg0^4nPffbAaBm+U)_;"
    b"M0U7D?o*?BQy!D1fSbxDgu%^K!(`KrOb-eo{)ID;m~)gZ5Tw<jrA@Mp)>xT=-D3H|JA2Nwn(NV8-BO%2t^gT;9hS;Psa%lj?uN$U"
    b"(>>r$HvG1YLT&k$PN`U|YF5|`wMPfxfK(LRs<^(HSpH+=I>$gJRhP&&%q9DSk^X8z$^atQ(LC8)lUFx}muG8cmC0kMS10WQzNMJe"
    b"Y8j|8a~ruhiM@$mE_<2$!kBVv67V*Fy$@keMZ)%sGarlWbbYX+P)Bo_V&q(ivUTpgq)fij$#)|QabH{`-9h3_-1NSO<?Hx$+R_!{"
    b"ZEsTh9Xh5ibpZjFX@8T|4h`kTO`xepoY6<JK5xvJ)NpyhGT$)FS!=Xi<&r~K$vH9Q7lE>{09{tA_H!8Gmew*Tpp^=6#up&+0z_T_"
    b"<VTf~t}^+DCb}E#osbjiJNYmKv7Wkfcx$ZsYM{cSh9}T^Ip9a$25}9-9fg)Js=gqxn{qshm!E7S0b3B(X6?41N<PXBd<GVa4*9dv"
    b"$f_pU6O?aGrt$o$itcm2CAtb!75Jyr^~KNRZ<`c*w$J)9m~%v$rMnxiFZVj}Z9<Q;AT*IN+X#>s<+GPMT=HD9jB9eq$IJKxc>Sdy"
    b"w%}Sop+`z8-+Qy7Q1)4$W_4Rr5A6YC;eat-SQA!=CK_cl-=;?&l<SbCGUed|hLAwhafwRRgn6laRQYAo1&T-P9<3wj6sZwfq=7r>"
    b"u7glpJu>D?tgSw?(3|WTldtEY%yyPr%=}|CNkVy^V1@OgeAW6Ude6OHLfJ&+@Sn0muSpvQa*ocKY6M8UljJ99mK<C!=}A=MEtXcF"
    b"l2*&o>QNvp7xY}2d>2=%B-y&4+usqXe~#L^j_KFp?)gI?H%PW-yPRJVy20-|rF2-0$d6)toszG&-S#fmj7$5wbc<iAmVvim%H=#I"
    b"8<u<@1Rf)$xV8iBwjSUTofccKVv?x%ltX^#D?W^DZ$Mx0{d(p+C8eFhj?Np!9<lZAmGQT@Q_`QLE;=Bk4PyMPV-#=PJ3#R!XgPFU"
    b"qqC<WO}rb=2oN*KIXe<YAjPxL^4IZ?wECp~+_T;+%kcK=nA22}HS8)2I*qiXgt-1om~EeAJGuY)75S<*w)!NimOE^tc*KC&u9Ck*"
    b"rAf9^d}#0Fi~#uYgfjVCPGu!}UPnM;1}&C~JGCv6t(UbliVelbtdgy>_RLTCsdmnhMx*51k74yke7P3i0pE0HGuh+7t3O&jp;SJd"
    b"7(sDk@v-*ApA^DZLvc^vGr-(BY%gQobDS?50uA8jWfhwo<CgWKsIr)If1|CZArVUp+FtH|<KkI8v0yYz3_)=T)T+?0eLVV|9irbR"
    b">{H2hjOnqLrQ%bK)OiiglZ^Ubs{VjcM>kQQ+d7$kfD-nyH0*B4`L4ViIs|FlcFbZsWvIUuFSlaf1Jb89oucy;^{7H<J)A7aLhmI^"
    b"kFgH<i?g9vBEygHt|O;DBt{}X+p)bTLu435ea>DfjmXdT?p~t4;*$;fze0Uo5$dzOt8{O#g4Zqps(8Ot+_nFzRYZMVtonl}>bpta"
    b"0c!zj6zYDk%OfQULpr6%Wt<X^mt2?<4Z9!4ON-QYsrVQY<S9;&2Y~pF#SvsPhH--I1WIteTM`E`r-Zdam=fg1;scx@<%Z&ueH(}%"
    b"-{1uKh9Tf2g2b}UZ#^%|6jc^;HX}}vu;ifa4J62mf$@<x1`M7Lq4+&;8X^i;&XA?udlxZy_%PVz|8giNix@<x<>AkU!ZE06G#p+Z"
    b"3dbP%Lzv^_6L@8P78YL~%fImnEj|;<za3{z9X*Bd-A*vp1!-!{gsC-Hv#OM>78`|Wc6l<7Ewl_*eYO&(W18oDBFrg{GM7AiF|tTh"
    b"bXFqI;7MV^#o5;G0seghF?2{*yNJHz>9;}8gQTm>e-4ng8f`{Lz&YyCmbBYO$J%XQEo`uj#mrUT;j63I*(fw0tsQSX=PKj585pNz"
    b"lYyctbj5(3SNXD>txhjxJ`+qqMrc2O$O2SN`h3r+tHio<cvq<=+4Ge=S$Y0gCf}H+%ueaY^c6Te9lII#4y5Wg0t?i3`Ck`@rzlyO"
    b"qK>MSDXJ^5<n~dixS3B;-o@c5>Xb4?{U=Y!?OI6Hy;5~2PH8y@VL(X52W~yuu=)dwuNhc>r3nd5&gM^6kg&Q~@i7?qbDW*N<;->f"
    b"x6|lyk4<N%`fz6B=)@ZL*9WU%Kw6dM%Ms{yNMraxtK>X@`;GMK*>(yzn-)^{QrVr2ng&}>f#mF*+vb~*4=|y|b;wm;0l4F1tBYv6"
    b"tHXATR%6A-`j((hm4n`!{bv%YFReZI6Ys=^X_#ao<o6o-Kfge}+@JU+H}*h#iR*W@C#vwLZwwk772NkJzMZL-Ap`E5#gvsb>`ev~"
    b">ABiUAj8s`+~l=^*<Qw(^wYJ-%fi#B{E{War{*l>T@#v4uMhc8p2xUC>!Sb&eEZJjs~nO|lpln($NBpi)D7(kBfSO4eora<z9ZrJ"
    b"wft-EDTtBuGDOH_3%Q1#mwUObAs~*Y_+zDbb3A*Rcp8MWu2^Ba7!=aykK^k(tkjjO_MvpQm>1N96$Oe%?H-K-RcIG**;a!EO;?mO"
    b"+eU{D)OroG@FEI_Tn$SxmWEmRiKm^axAOvUEi=lWG#=2wT5neUP<4t+{w;q3+kY*rhEiOLeq5n{a#p)EYd>V$`@&kBnlg^_sY#mk"
    b"Jo!TyDvurU1UE~=YMCB$y6jC@ini4e2BQhXISi!$!(<ofUu}AREk9as--}=6Z2%8MS;mXXYL5U!@bNm@_u>zw*0z^Z+Vk|C>k)8D"
    b"V(E1GQsjrnXkH6LozvVXq~-&MpfLYf&?lrc12B5b0_hizoBoG`gmVC=Tiz>UE8BSi9SP4tzS{5+sj_~Sy*QmB)dA~jP<JG#pfxJe"
    b"k|yHUbo|mC=las*KNoU(GeH1<`1)%I*_(cxutKL#uVNM5z1?SgXPF)g+iN_Iz||kDNoQ%8(dzD)UofUt@n}m+mE43?NqPajoi!O1"
    b"7%smKRX1S}(~G=(OUtg4Jno9=sMB&~fr?gOep&a{bE_!Hn;7`T&ybbtelabuRChy{R6Hsz6&fZ5mJafpk!&iKicjzK2u>jP5=cJt"
    b"X)M9bggJN}%QBT9qJ%ZMAgp0Jlf!aoo7v6qWi0FA7wG<g7`1kfr1V%0xuq3jmAxFmn(H_dxrR+e<P=z_h+P?OwNM&Z6ihjk&$^ZN"
    b"ch`Kv0RbLdyJU{KmR`(Q8<wgYmTKAywJPQt^^aTu4Kh5A8lnTPLFgN3rWXK~T;gk}obYu6$~-|_>qAU?p&EK^5PH927502O^#2S@"
    b"oz_79J@EH>Vk%F;7w!v4Q=eIdy~Ji=+V)y4l%i>$pQzRNn_;x4SN*98BO3HmAflmY3h)k~CNxGRrR{^S{rllh;DMmDRR}y_ma_fL"
    b"Vt(Gfbp@)bPwLK)^3llw;a8Xk?Hr&fIx!E4wrYUQ+6TX$t3VXRWpdsK(druzb_GG$3|~h2>VmI5M43G}#*iM%=5u;HMn%X)^KnR^"
    b"XK!yWCz)Y)N4{Alurv&HOLM)Vly?$7`!B1|;5+U#$g=k&PwbYSp_kDWSf~6iT>tHxxj4e6B9MWalOAJ7;ULPF9ZB?1sc@9wI6RL_"
    b"Rf!&>+y>vM-2k=CxI3&9q4J6KN9k#_cY?AD6RQ2YlvbpawODr|ni!R_NB!;7q4v5l0T6C@{9&>b7PtRh$~RDpb?gq-p)<FP;FeBK"
    b"v!xS?^jVoJ1Fwka9%3!u8xFD_`hjtHq{bLntY$T4tEJT~Em<&D^@Sy|`g*q1Y;{Yk^2gXj7?P*^(=8)4CguWqpW|-<)Z`YhNsy!J"
    b"6xk&3PGU<<(8_$JLDEta-`*?Kv86^!OSMkhY-s^-YP8Z)9h=AsGjf7%mRq#2{-9JXvJbt}0Rpmyyo}XkWOeB@ZppNam78Iq-#wBw"
    b";+BNP3n8Vi2LK~Y-Igw|t)yZG2xb-g(x87Hp04QM(K+N73sE<KnO<%0#qYvQzM+ZoAm>@AuZs5)D}+XgwFfos?mo99LOwi{(Ycu>"
    b"YlL-tZ}^N<Xrf;zCF>B3u=-|TAl}*R4!lVYEn!R3@pg@A=c4z|E+ZW8geAz*^!H_ad(W0;5@xIN$7;R+iS0c?4Ds70WWg?w3~N<8"
    b"c5vR^n1&3y2|2a@gj(C2(%RCSM2uUR8i3QU8;RxgY?d76_l;c&vrieI(p!2(DxWj`1}a^m^m{RS`_nYX?*_3CWw#4X?kE5(8jhOX"
    b"eR>F)J&Z<DMv+|eRO;=s_zX`|yJE^QTnO!EQZd?aF_>w`J4_#$nMnw6*h`cNxfqJp@%u`a7RuZ{q=+gZ=_fMZD<V>8+L!+Y=EFYR"
    b"@eJKJJC1X{{1ov7WrlLd_2?yLK*iE*2measO%Tzfa1Fa$jy{Dga57rLS<RdC5%{Ge4%vbwxkicRZl15Gm*Q#7JS`02x-lJ$->Ub@"
    b"Y5fvGw>lc#YRq%&%MhBz*-TUB>qvefI=_JVe-O^kvj+9Z>)T@2b4Fqr0o!O9?(#V#-=I8S%{RbteJ5HvwqrlrzYO&=TWw^;FdUhQ"
    b"Nie3nBol*P0wH=%qisYg9%$@hV~wA)(+tSg=!U<2nlFCF-oyKp|Bid-?E#a>-jkezMGJjc2Z)98Jt*o2xj}6Jg&>iCNh^ub2n_EI"
    b"hG9Sepmu<P1K=C2AM)k`0IYhjv4_3acn&7hHpwRv3~d~SLmUR%ptfDI4YKy7MF0S_24L`wHlfUhcKcBI>dufg7``bxDCN}x=JxJh"
    b"6_Pgb-~MMK92m`At{i85iJH;%ILb;Jr{cJCu~|s0Wh@WJA6n3Walf8Rg+c!x)G6m${+whPkSN+WS$=Sk?w>+5&%v{Yq`Q{mu*RNL"
    b"*w_;q@FToLiBdICjS}VF{)3jjMAktDpwe)zm-GWrgrya*Z}5MFFT-Cv<Zn%6EliI>f<%dOj&MMTPc%BzQt=2Q8p=AvIZE;9j*Uzo"
    b"2mNUU`bqNZU%-&L0PqKaEj8)@_>cIrmF~WjGkNC$AE|!(cXN(Fw-5V9;dg*_3=c`OunBC1m~*gkvD(tPV<KBA<{W7(RcjAfI=6og"
    b"+;E;ctJCmeyWz$6sEj6TTGkm}DzgfEsj0S6yyl9jH3401Aoo{hthstbo^dHD30kW#<CeZ;KnUS&__V!D{v{p?F3Vs8{E@-(2Q)Bs"
    b"JrJl-vqM;G0wy%PNa=wq(#RCEx|nUmWtYg$yGH(X3P~0IG3_ooJnHBkk>-pw_f0}Mc1-XU$a^md0mAt_kTYw?zU0vGa#)w)#cn)2"
    b"``q80!1=qR-ly$5OmCqRd{%kYdBtciUd)70F@5-CS<W~wf5JHVN7#o@0%Q*wdG;E#h$+qPU*PXZkb6?0j9HZM@cW+v<40OJ!dgPz"
    b"Da{H2@tdqeWF|$TG?4m)whId~?t|e!+K{h-j@Gm`<f~zgoO7^!o?6wI0#kR3T{ao`=`SCeO(@W6TbXmz(#5(B{`N#v__YfAhKSto"
    b"VrSM_e{-TTbn+rSvlmnC@LYIw9v%3bM`u)Z+y5CTjD3Wol<85P9sVL`NSZo87?Nxw@5A83`Nz#><^#FqYYKpE1%&)Sq1w_~eG{9C"
    b"Q&>QEYxfxvq878&BbJ_Ofpzz5*y+GhwdGLNQAWi<J}wi-P%bCiHp7eWWQ{Z(psj&u@OJ6B5Zrz%-%QKHBs4v`nf?R#Ste1CTdmvL"
    b"gd+QEq>=>03OuW2dX(ks4;mhQlI#<}6zK2MHK9-+$bB2v3rwJ&Il6jWc6qO63xvHGEtNrCn3)P)W*L#lx1+7Uh$ZpmW6r@q20)>^"
    b"boe8Oov*eACO|KnXo`m=lvZ8K4757*%juF3z#6DH>)sLSF|4S5D3I}M1c4viAmn&KxQPI7Haz;B5a86XF!VFWgZ?U3s6g)$r~oz#"
    b"D=M<I?<L?50Pu-n;Byi9$r0dlVt`Kq;3r-fc!GkNI25|KaX}Rj=tt5M1kO>u!0P*VR5>-UZEB#9o=ZH0(|oB=q_o=iMPCIfx+ua;"
    b"H$6lw3`bbn4gUYc{q6(=ejH4&dBXU3xDxOn%@Y6%Y*x4rm%<Pt-;R!pqG5*k4bT800KjZ%5B1?A%V2g60sQ3G2G|@1c)V`wyePa?"
    b"N#6wCQi16R)PO)gFqz`Bq*A<nM$gUl)Vo;k!Xm1krZ0(t*-k;qLoYrUm;JhnOjH#(oyo=oeso<t5^xT(0Y{08hj-$Yl;V*lK3R2!"
    b"CMsiAH=m=JbI|Z&7f&pu(R_7HLU_KK0SvhixUrPY+Pg=_nj02q8Wtc!=8Tw4h-Sn%m#vmRO!-=K8O&j!c_=gqK|TAlaWz~YR|8IS"
    b"zLdXhnwypKb*8x<_CBBH&c#e~=`hW;CCI0f!_(Y5-)Ne9Cp^tzbA`C(&K0AZ3mwyhdo)>Rq32)*Q>3M5LWJfYF>+uHkKzs-n}zJ)"
    b"RoppYXV}aykwq-@4MD2y&ew@f`*lqCk_H9sKDp~M^MkuW<PNl65Tf*NBh@HLc|kz(3#5$tFp*nEDqreIz%L`I6+t~YemB|NpfMOf"
    b"E7YDhD~vllv!nRxxE!U8>G_=UE6movicNHIkbe(U%MxFsDn3E0HIk`5en`e-y^_xg#18|xG(>?dmH}JLRoEh6&fxzxZna^HLcFFf"
    b"swHU8i*shBIdgPRN7&2)K`K|+Od4l1tu)TJ=l8dV;lA!`z`aZWP!zZgk8H#3+gZ3zDSMEEA_V~X4za1Y?aK0S;S03bNxULN)j30a"
    b"OOw5m@}A|;u8FjpvCPt1C1ka-)7|HMy~Npaj({KmF<bdQO<+av>UX?`oTF}*u}s@WUf*d(C1$l6UTncZMpWs_8lm<m5(VcZ7Shu`"
    b"NNfhzn(RTLgtIl`H^AF8^6k)s@F>9M1FNyiw<JUlgsAfpyqu+@D|8tEAS`W7QX*TJfl55R4h?e}vj(JFm5WmRzM+n;NWlPS%hEx_"
    b"T9!$&RX~@Y(_G+Y>Oc_)PSsbkT^XeTohIjK_Ze)f<qJiyYN7b5ljq-li{6hbL<4b8-hvbE1-8oiOceS5+g6!9EwWX%J14SLwlgPo"
    b"tE?g?v{g2C^Z&|L89oPdnSmp^0cXpk8Uf_Xf`CxKx6sbJf95nQD2HrIMeSME0a+|9h9~}2MOQdkV!)IiwP`=XH|_r%+O!|RP5TGO"
    b"Dtlp`Uz+}wI&xdi(ot1qfyK?PMeO(8=cLslD>S*;eES$4bcyZ`!J$(1>j3i(+QL#73apLnS^PGu2S{dxTb<$P9`Ow@$O%9^Wa+B;"
    b"B}?r7vt^{_1-?;g!(H2@=~hd}u1nl%Q+{A)FlA%`>tJ_SI%+;WzroaAyzj;eOspCZbT_z}I|IT_xAtT9UhUypzH#Q3(%Ibts}zSn"
    b"(tgC+q`N^(GCYBLDcB+t(*$PbTi&|}Lf%slqG5{^gcK+U0Sc?y1vnYrRm^ds14sZTTf;bcK*7la947@FCzIG1&?w7&(5=pWfa64m"
    b"gAhQeu?*C_#x#f)D81%~95a>afdy)d2GOD`45MXk99rl;07po*4x3gW<bX_nr?h$$@N(Jk$J%yFfhZLSh9~fW$lus<!{aDb{#{xR"
    b"O^3|mw4SXVg?7{~xlCOf5H1VtM=gqAV`hFVHbSY_ltcRX4Jm$KLL@P=)TM}|4I-O`TRJ%h8;dmB(>Vtv@-nN?Sfpj904|XiN&L65"
    b"NWJ@@&xjXkm_QTRSdqGaZO+lM#&nvr0n>q<>bgJEDNwaom-`i+3DJDNhaSk|{1!}z%(gVKNjgdg^P80M70JSRRGR5otYZzGGvyp)"
    b"bX0{<%_M02?dK%^MX;Bn$Vw^h(h!7vs{MufhW8s+s5QTBSfOsWYShrMm3y&3LS;n8wsacm@5Px@_$nd+Dbub_nR69^XcisKr3oRi"
    b"s8HK&Nu$$23Nt)`1`3;KHhqtCn`;yji`KD$BsPHD<^dovo|^Wg>7AIRy(2+T_8AS2cjFbK0rs0+Wo)cFNE7jSoM$p}9)6BV)TZs>"
    b"XO*l2FLB2+p(cKOSqV&NAI=$n0>XP1sIAY9N651XnlyyQ3asKu2Luw^-5N|8C`2nVbWGV^^GV-rV-X`Zb$QRxmVB*h$AkP3gC9}2"
    b"E`FBr^zZ+UXBlz#l^keO2V=_W#t5*7q5-=YT&eO`A0sMAPLGCe>NwD$-lQI0Lkwh;mdpCvzum+a0WF^<gDh4p@`V7YUtN|i*+v!F"
    b"Beb^@-q^W{Ey&=zIw)loG25u6Ep}JuW40_KP_E{iIi?kSFNd$>;x{6*y7-DfS==pvS$@}qGWl~e-_t=oYRgPTAepiSX57euMP5MI"
    b"x+@hQ&9rroNS9k9i#bF6e<K&oi>#FDf`sF(F*v5(vmwB8%I7VAO0snF?($8RpZy)+H!64R&4rdfi*W?NOOL^Cp0c<78DB#V1DH}C"
    b"t*>~w(E7t!rz88Jntj^HQt@wv|98j!e(-BA4*!HO{2`H-r9~>{M+>}qRG}9+QW(Nb%P(TVzV;X?u!sjcPXYS`fITNavS~TMOH{z-"
    b"o0e$`*q<b@vj{kc8Ni42?1x#Ovk!6QIV&RQ*G$AmS?VzG&>;#kY~qglE)43!NB>@+;ytQP*8ct{YuKR+Yz2r}pYw${RrUUf@|BVO"
    b"W<HOG_z4~Zl`%RJ!b7V^kcw7|0ldmJYIn#9f5KxbF>-EY`mGXx8`pGj#t*G*xD+rn+D01^q58swQnBb844p&iLHPZ7_za34KuNQ{"
    b"(Fv5Y{xIT$D%SoQ9=`^j#M=q%GJl_t)wW2=7wV7fI2|&tCQrE<0QHGn;h8Pncd1LRxQ@&JL3!y%%GE~`bEd<LtIJ`+lOQe#--pkD"
    b"@FdecnJ<ZG(s28<oP+*Wp;4C&VbY>eOq?AQp0oyZPg>e4Pq1QRV4m92vh5luDPVf!BB^c0%Hxn6?+USV+b82~Pt)xUCRpU9TUqXF"
    b"AnsdQD^D?7x?O(rS^&NS-_Eq58oo8<nPV%@JCAFm^<hqPN5cAb^RUsidvoEVK|lMxd8)m+@JC9^hQFcy=I@vG&H#klffyP^hx`hE"
    b"anO-ageB1B6FYv<wW#Irh1a6!?v(t_mHaNsDhTCwqh5uOy=%cc?%gOXaqnI5Cv-OoGe+)4VKm*1!ullr67=HTC=8cTWpxt<F}<Ca"
    b"Pj{mzPK%nccfwcrZdCTYl;lke<aeXQ@ZBg~{M{%lmF`9%IH9{ySVH7(6hTA@@op4W`gQL{5rFq-!gr$(IRzFfBK~d^wV&=rAt2B-"
    b"7q}axqq|XJ)ZM6BNPp^{dE?xTLIm);QM2Kz7t(YjWI}I0kEzq9-;4eVh~ammHo+Ia8?}{siOs^a?X?eMx5wU%!iWa_caXU7ZdC5^"
    b"(A}un@U`E1{QSF7vroj`jlw*UyHQA|csB}Z5${ILq}`NkOp{=RIDR)u1rYPQQAYUUccaqbi|!;@uHf{T0Rf(?<QZ3>;Dw&OW=;>0"
    b"yHOab+>OeF&(Q6pGt+>6GkN0h-6*V6-o*_SzqtxV51WcWUifa*OVc8Eqkb~&>)(xfc-pvkqXev4xf_*PF)wmAYMl3QxHmvcIa=Ra"
    b"I+VqI)!n84Q)~N}_nOM)#NW6Nao7LoK1AI8kS64mrTmIg6B1#W;W1POf&sg>&2B=@sc0QPif=iPiSq5E6%`mPza14?L_F5_r~bU3"
    b"BJ=eYu{6xjIZZ){{Jq!`CVN!!qvvPuBRJ4p!eq|5`xAo+7{l}kESr^0Fabtej*GBlC{zw!DV7+%L`e*f-cBz^@SAn{TM|%j(k@7c"
    b"0o{F;?rjMz^5lL2{#e;mtSArR#5)s@F2z?lB2Zi1AA+Qq(}-_j+kKmwrX%eakJxj99*slF!!(j_B$#GC9==PJ7H|&IrSFms+u#^p"
    b"A+MbQ#Z9M0;7q8;?s9}PSlYdpotNG|gX<S)nn}&ZN*XfM{DZKSZ|RW8XW0E00CmnR{Pt~RX#}2au*9RWhkzT51Fm?4-$?JUjZkHO"
    b"$b#`g8L7GwmpvM|^V7dX=`kr`s9i9sq9H5dfKgu>>hbPR-=YvU36C75fXw@up1^euIy{<^js#3W8>X=!zlF7WQv)^*haE3(+>9_#"
    b"ZVrjVRT2$!dQ4&sB<@e3VmSU;8pmjIG~6H*DH#2pDvZ(fN`DXHg}Dnt2*5dceI;1mw{N&uZ^x!}W7<eBw+rgvg^_t5UR(<PO`Sb-"
    b"{Wt6E_Ul8P&A|eBHs@%AkV@UzIQ3SDuv*&p{tXbV|Ar9Fygr8f8ZwOZYt1>@IQ13?4MF3Hp{@%-6QYw)>A#tNQNlVu!;dIK3{^E{"
    b"hke943+xhkWF#!!RE|t~4mD8wt6IWW@jyJL21709Tw(6?Fs3j!ueHRkP*<o(ouy?Q4m5Th&>6zT5fOW|67~M8j-qjx`gSO^KN?H>"
    b"_!7#9`gmeF-bkoEj+Q5`iyZ^>$R#okNC);f*~+eq#b%>TY!H%p2UE93pmxb~&jf=_C@k9Lf4dyVwjz2v<UQymDTgk77V*`9szlxa"
    b"5lxCXWS2LhPmy={fk@fq{L<%oga9vn7G55?^f~wPm`k5omq#vr&H&Kx(r5hrO^!j4-~S9FOpQ!nRAB<PQF-097rOr$&M!pg7vl0?"
    b"d4c@UpESSI>~46>NC$E>$-7G5B36tu=PrXEr#n6cMooH_j_`ChYR?(M>5e#$R6Y7vI{%-piS7KdC<fSp(_LKpb=Pp+Sr?h^+C$9w"
    b"3{H1>vHWI)#*YGA{9If-8X85TRM}u=EWatUM+0|$`U9Eq(_QedOm{8-akvE~Aj9s}<6(AQ6lzCeQG1>wF&aV@hvv4-zk=Gh^of~Y"
    b"AGLUh_BWySdslxm)NZ``8%h$KdeMH?<c73p(Xc5Z8RDtfF5F56>9CL}fA4x)QAbOL+OLAamE~*t6M2a_M}~by+$nPEw1*5Y+C-k3"
    b"GKL10qAwv0!}wMdA5l%w11j%-WIW|x_07gp>Q!IA)6e~_<LUV;zgeeyul%Ot3AGyiln<vh7aC6YM_@<Per@RgWWE^mmz|gX6|<t|"
    b"FGd0xAGOa###2}r86jch0>IfuL$U?0Y@s<$7%3}>#ch0sbaU+V*)AksWJIlnEEimBrNytcPVluB--Jy&Z>^<KMpObXvDo<jC+rXn"
    b"s8+*^#Uf9uj~Y<ty??!D9z8+~i5Us=m05eQnH~!w8sxHxe2)X0Sl{e}p(2JzU!=#nldcFov2EgM=>6*@%A*ntihBQw&)8jMEcaR5"
    b"?y3voZjs>;JojzFO(9RB2PBJxQ9LKApshFDMDn*MqIxVIvI9+Ioc2!4InwA-v+aVm)pFYRIisDWoP&)^)mhyo_MGNMd;z`*AN6b("
    b"puwoRT8EoijSDo6fT=bh{Mw4cT9)uOOrfT6nc9Cq)O0p1RktrttNLfaG8$LutWuD-^S!i&LM^@E#(Z)KSBwHV8w%CZEKDoSq&DRo"
    b"Y?#)#RKo$%cIPznO)mhW5em@NV<Q$y{I{_XEd}H8?<6MB1|S~)mN((<6Uf%n0z1{xYB6;BtE<cXigvx|^!Eum{lz`2U_v(WDa`d6"
    b"A{38(b(B=f_-Z!oYGIsYA^>S44G(`2tTp`fw}P;Yr@#0WIsL^Xk<(wyJ?`l*mWXG+*)*n)^RwR#{Oor&!L}*_8=n2rUZ-;QOIwd="
    b"OQ_z^*)Q#WQkZh~i{j+hKl`QBB$|fLewQeeZFv0s*t1`({z7NJm??brOIyL?pZ)UfS>^0k7drbD`zq+{m!L^QXz1*>^t`iQ+J?om"
    b"-`P=TztQhq5U+Sng1zWJV=R+=BZfz^(2U<vCVWX4c8Zo(!|wlt$#EXUvYB6E_xsNoD?he;Wbk*=)xelea1QosnR8IdAKNE<J2;Q}"
    b"1aB7QYtLHps88}Pyd!<V4L80c-PO;ZnqR~6I4TlCJJO~FfudkaXFfia;XCr79qA?_Y~Gf6mL9_+i%FqBhSH_WG^Ez1P1M`Cf2{5D"
    b"B$hbjw}*krZlzEx#owIB>)gAQ?{Whx$T<?2sj^Bo5n6W((cOZ;UBRo{l&g0OwC|ADcbZNBvJRnkvT68qD2=0LIW2p1ZYJES9buhy"
    b"hq2Y6%R#xf@^b?s<Kd6AEtb~3gtvtXX2-$a1&Nts@7tdc_V#JQPpHIb!m_mQnlwI5g>&Qt@v7VC_UlpU7w>eWm@57>EkZL^OAD-T"
    b"DnDW)FstE>4a77M-3|@www#sH5cvjw9Z>4)L`wZSX*H74>JTZ-$skfP)Z;suS9gXf$={bA$WQ_2!&r_8BCgAZfBSbJuLt_RIeF2="
    b"9ze$&69Mk^;2XU(&P=iC)(BQm)xt=BE;JE+^}+2rwt7SoeuuvPguOU07k2PSdRf_xIt8$d?IP>uNVA+ZJn|cSKWY1lUfo&uQcbHz"
    b"nVu%Lv`sVt0-+^*3G~aUn%2|Ji8)91ZX!Ole1(RlG9bJap5&}9dx`uZkY$rVD{5VR^DaF<J$OK|6p)88wET86y$ODnNfZRsa##IP"
    b"pMjZp`_ixp{i&>YL}{bMk4rcvXdo^uifZ8+g1($La-W)SZA9JA{J-&j`St#>@TJVpCPXe}{$WDwrOfvygf3-nO#I({zs&F2`Gdj^"
    b"J0KEmL3)y*1u#QBI0nT%NL_yNa|B=D9X`P&?;Z;Q&B_J5*10$^f9IG4-)fO{bjwyM-X9cqtcWc%ANZexlhK~fN$HNi<D5r>3W;jt"
    b">M$#H)NtH{u8tOobOVGm5cz{fD0N3ERsdxuL)kioNN)|5KJ3wA=~u;--ul(}r6<!B2jE`3Naz5^M5V~zpXNmd&D#V|LjP^7<8?G%"
    b"l-cVaF>lw+V;{12-v7jZR=r~|Fz=iv!49?l9J0K|ja$8c0`it-okd`tJ{<w(|JJ4Ab8>`!Z%&HP@6}1M^m}Pih<<;n{olD%?7}J+"
    b"t&v<ne=d_-ZP%6W6XMScgL)Jw+hX;Zk}}+~#wFRoKyLO>cY~oZ5heTg3g>n;*hHTQ9{BW*;FR~9tZv%gEwRh{xPe6Z1rP}=!`p88"
    b"dbu9rxh%t#hsVEPUUw>Ef(qpR)f_BE`()skCx?Q;`lDa`Z2J_tPQl&?U`XI``dMJLv`KR+|JYG~@+>k(%)*{ZKo5H(0aIu{l%7hE"
    b"QHxx&kcVfsmB050rE>pGT-mi)AC#(3l5U~d|E;LluRpr|242@w0W1k`hI}{T#j4?_0IN=|{7ufmz|&ZfR4hxyy^`}7vmIlki5;yT"
    b"Gv~=bt{PUnQuPM`U87VCved7Uq>E1l=GTn|0;}*~|LK#YiEWUG-6o<^7v~6`YC2D`b6ICwf|>>Xpvmx<4WGUJcKhl;fgsriSoHuq"
    b"WH~1li#u|eni(ve+w?BGL*7NpCSCuf+YK&<UEa#Q!#${<yS^F53=ENC(cd9h&Ta3&DlAMb&5^YJe!=qF9Y1BZK~_D&oTIPeA#G9C"
    b"8CZ|l27yegM<nNHRVwRXBGW(v0MfoPQn1s*sz1PczqVdjuq@9BT3UT(W|LW$<-={01Es+^sXmddHcB9@=&b%0!O~HAN~)IGVaUO%"
    b"k68g0QmG)>dZp@PhDTl{jaEihe6s#1OX?8tA&P4I6c8ldVaA-J(3J}tS4~n&ca8c!!+MKPvdOUWOq7IwqV6-I6#${Zlns4U`2|Ef"
    b"WRF%+XU{dFW*Je7-taK1KE-t34G7<5lO-cQPBO3$19u51tF{W3F3CBt!^R9uV`<rTwYFXRo~3=eq0u-u)t6Yb(9*tRkU0k$RkPJo"
    b"n*F_+qW($SFToBNBW0Nb(MbOfMDFjmV_Dj7RMs!fE35it%Wo_7ECu=?S<;g2V(=sZ<i#RjxGk$A>yTd-{KrQ#M=dQ?vjYnROWQUx"
    b"D;{OG5r5mLbQy?@((HMFML-hBkP<387_~S>gI@)Rmz<~iYGGD@0LX=ETt_8TSSzK%s--~5<y3MJ6~QtGXAvkGmR=}iMfN-B)|S%P"
    b"iH*j_%jUkXH23pH75I9}r!=p`_QtXV)&hf0l!|mx5&RX}n3}WO%#X%MT`%4Lwn6Fskzg77$g7p+>40n05BaWQTAuVw&ln%h5=4s9"
    b"Jf-VfMHRCE<GekPOIO9p<UJr8vMzR5x|E$|-8s!64GRYZQnDaz6QymD%$9B9t{d@r=I1q+!@4;4yIF_ueKg4E(V7{ebFg_ZyZLTm"
    b"^8^}D-}9eH(zdpYX#FEXl?GNYXH*bele8ay`ja8FI)QAsv&AATU<M?cu1YKUbf~;mM;3h?^6!2PATJhJ4p!U+!{RKAOvTz4NU6uQ"
    b"0Q?uvqn6@_1@>On;Xv+d=YhzycKO#Ijs;0SG^#%Ym;qIb#W3LU_f1aY^CC-)P?Zu`p!Njq@^&1i6Y-{}=~Yy+9La+H--5inj1>ux"
    b"E9-F9J6;1bx&kvT08C)!FTVIuIYh0=dS@l{?|BODgV*dio*!kQ1nrsFgK3>)XTm3P`xtyUc=dKUAde{qOhI00Q|z(Y<@R7mxik97"
    b"0H2ZOqcWPYYR}H~X#-0&jj6R~S9ud^&))1yYFwe-eblRe!RVW?`^a0|H11ngt4cN0<?mH{ZqjL7Exk!8Bl1Htxzc2yIq%|%hBNsp"
    b"mz>CzDg#WnRn$_*U`i+?vtlQOoCt?pQn8gnx<Vm7t^cr<b+pJ@fA8#+5&TN@LuDQ3+ncRBwN`_+X4%g(H^GOitl}vs%PF5UC}nZm"
    b"vyC=&&e7btzAGDTs=0063A0yg47=aO&6qcv?eb)<T);1{?N5+jn@IM1XGrri%?@WUEtibX_=7=1J=)8v*hA&-4wt_hNwGq}i<nPk"
    b"ZiOFbiTq<dH$1DeeBs^5#>gTa+M`?OKcn^PUGk$L(*WMZu3*}1vi7Imey1l`T3U*hxhmdBB6IRZxbl@&Wv&NT(XcAhE3d+5!7pb%"
    b"MFnI?h46p6RA}z|72c&X{CO<c!Bx1K!k=MdwumUSw3!L5v*P)2vtlUaeKi?|H*zy7!L$QP`0I*M8MZw0ax`$Gm{<#jERikAoTeB$"
    b"Tb?<M3?A_mO1z>HQ2uF37-Yz@9Kg1`1AzMy=d8-i^*#j9WJ2w;9VHQn^3`PZ8f{x=BBUXRu1AQL14Q!yq9p*)2@X*N48;r@B$$Q("
    b"nt6(AqD;iWR5Ce5!5-S!%(k@oCITokfl0VBB$v6rT0v5FG?M;9H9nI5S@m~8((YshBy(9Xtq4gDNYLq!m*7V9^33IKsW1_(ege%E"
    b"xnVV+R!NCcp-}=s7Z+Jlxei=%$k;D+HRla>`N5OK6O?kpCV(jo*`Fz6XQL@Jp>ji`CU=!r$i3OOvavv|eA*iew1Gw1-OXMjgy?c_"
    b"_KJ=9>ipf!zJb~~D(@}a<GsF7eW4^t;DK*$zG@9Hs5NbSTppc#*Q9an3+m*zCY@(r5N*AQXruRB7-WZh`_Nd(6eKJGIlZ?jDLiU!"
    b"2(n}xOOVUfbEBZm-f*s_+7i;Axslz7M!UFqpHj5575p_>@Cv64=x%e!zx;A6Y&t9)<0=bhK^`3n#%qmVg_&MB82;omuZ*&1CwNf7"
    b")*Bb#@IN~d!{L?rVE+YDSD%QR4-nt7iSTVi3t5PBhX?qDVz3I)UX&I=d)+CW8W$r!$i#K0tE~R0cU`GGNv-fN-&OLzpFmE7mv7}K"
    b"=~GXO4`9`G2QY7&GLTJn2aF$6ZJU*tWeKpejQ07NQ|H2;X*a>2D^$U>ebA169AhRsr3$9Ktc){!lWonzFvDYyas%6FYl=Niw!Wd`"
    b"XINTxX-I#-V1ycOmCqeVm~?S4Sz2l)%e@qJRXn(8{W(NiS!aM~J_2#5gA>j>L^zSebVFbH4)-6RC6Q>nO|U|{66Q8QU;sM`e95ce"
    b"Pl}3jedweVycnV+hc4pw({)_Q+Ru5CZvplMM@2#uKD=d^P#Kx}xd(g`a+(z|XkLdpRC#v!2^~K-nxCl#+#?LYYY>RJ3J^WKv`Fp{"
    b")0p2IBAn>fk$n}<l#aw7pswTRE}^q6vX|hU;F68Ql*cngPP~*T2<Qim6?KC2F*H9@RAZuVy*H*17n!06+4r#N{LQE~Y(1MwI)An6"
    b"_tLM8o>AUA%I+Tx_J#$rh&*)HipPY^U~kwTwim(GKZ9)EVH-WRA4f7Coq-6C&q+(<=ZA0yR0oom|M*uZxGfTR4%}4Lu9v1pwED)>"
    b"N9BVARW^$Iu_!T`nA6DZfZ=Nbe2iHFQ_RaW(9Mz!HyoMG6my>dvY5Elk%A7}DSo|bVBf3x0PdhvjEl<<^rr&#rvQ5)WTe}ne4|5t"
    b"G!1;6%yvqNXbIl~g7N_@9RgEiWOfnLmoPgB&7y~lMNHv<MZK@}pPC8n>9F;1K#uKuEg!2w69C0J309QO49O`o8#Lw=z{yh$@}H5="
    b"-7wyUD#$8r7?kcG2{oW6P~Q`7K!@#J+WLa!S#cMjO>%w^uyxt-fq!a={6GpMv{&Fe4BNY;cDs61<((X+2)4Q>+%x?Xn5`#-m3Ni3"
    b"tkOT&Ib<UYy4GEP(2Eb<Its|5JU5(J=227En;iHAuE1zV4P6eg1W82k=t`gjyZkAsA~EB#;K59lPmiR7WF$Y08|X-w8SGo;;JxXJ"
    b"0o0YN<L${iA_hvKLtJdD4p^wP1eouqY^-V)>ibQQziT2pjK-y8n$+}4K-e><2v$FqBC#fclCaMfv$6W4)rS>BgJcB0P`X9B!BU~y"
    b"Ay~fLo*+9++}>S4cm?K^fKZ1<=KQD3XyMUS_9|{5zWE%CTVQY^uriQuP{hRofj4B3<wuwhP)^a=Q5buHqy=bx^qNF|2luUuOk`#H"
    b"pIS}`+U}MUVpezH@qcRj*K1W$k%_gm$VNITK@xK`Sxd;EC7J|AaVrDmHW(l;{RR1e$Zg?yE|W_qLb;m&9+(#JF@WI}E$f=cFOd&D"
    b"GRIz^61=NxEh?Xo6YSqcrFzu%ruijgiZ9)xaRf?(9!&|o(y_}XQtEC-v!N59tg1}oy#72g5_*^$y)?RW4no8TzUg~cduCq$6(ou^"
    b"?!l^RPZ(>@8hy!-V87K-023-3fp4FRwcCil4%KpqR-ut=0BNXy6Vr2;986C@Ek~eA0yY53PCz;2T{B~Vf<>6Ee<oV$yn_RD1Of+I"
    b"{v<Yjp#9v|e|g=X2%<-^s!U_9(I-OuD+rI<GUmI&T_5!3^x;`DpzkR?aoqhdgm#5-x{C+8EyH{(B^=?_M;Xyv5xu1HpUOmPol)1n"
    b"36>yEm;YR0nc;C%+gNw55!XvkqS7c<m6;3uXk{~hNhWJgqea_9e^67SE|h=z2pY*gDtTcIwF(4jU0YyYkacT+(=wt7=o+;xkaIqe"
    b"TYA7`4G7(=3#cfo3ouXwbRY38Sr#zuX+o>kQWcDfpKEICoK+BR#|iTa|47hhCS%k1q=1Yu%J%w@fvZIAjbz3A?T~$XMe2>VM6bw`"
    b"Xl~Q!s{c!wVK=f9ZnT`P?5@f*)gSfEAUQ<-0FQAL(?FNVKmI6Mr~o1EElkv(2zbe0Uj)!>q^r!y#TiRS<rPp4Onn2N(bOkbd=xEr"
    b"KyDBiuI5R8#gl|);WtBDH(a6(o0rAahRIPP-$Z&-MQ-|3Sq}?*?WA&X2`XnOEHmJ;NvIv2>$_BW+wpHDioGNMr&gGd>kbG}Gku62"
    b"IQObMhgr67Vr?L|rMAdo0~a8TT+`!F9Ul+(u{1skN?00=0ubwg{-J-&FhWUrY>B+{78(Ws(QJeWN=YDqcu_6AqP7KkN^EQVPSjY`"
    b"=QKC^k@hKywb9R>J;VqUTb*e56{K1D1rK4R%>|S`itNfua&GM%D(^<Lt7>$XHeT@yVfRti;hotivc9@MV#T|k#_GJ2=1%m9jYaCY"
    b"OV!><q#eO)u=WdcCwei|y8EE--P+kIUj}Zo?j~*l5ryhPSoJ8sz8|ezy$0%5B?p6zcyoBDXG-(cd=cY_COEX(>dAA;_Zj(ifmlCe"
    b"*!>i4ZGURm{Wxv=GyQI8pnFcC#_&`#8=>Wir3FTW(Kpd9-@*40_VPuGuL?<{{vgxuEWw7r+;@r045**UyDDsV6u5>M8u;}GeOGw|"
    b"d6@4S?cGVm7<Q-P6EnK2qAZ6fRkxC=R!P;bib;ihJ?l%D)_S_Xf`#kV>PVX&KZ3Kl1qRkZvi@S&O}aWvF9mX6Dv>`r1w$)|58O*x"
    b"2hQ8gf@COUA{zk!KMR;>f3l=he)5wsWxbX_P+(tjQ`_DZIFH%o)%n~I<`R|Qkj-*<%zEdb4dfD+yksKRnKpm328~X-JA}<D)$oT`"
    b"kCeHBY0vlKHq^pXW6{hp^sBIt6)2*oOTtV2^|0nUQ9o3z8U8q+`!Aec9i{TAz7U9qu|~<XuVel`dgDb9_Z0_Y@7Lg+8jL7oiIB$y"
    b"Ei&P7E3=o%bp$GInWnNtHxqWc^YT>QtK4WZ2+s=JaiQ@WylH_2WVHi(9qz#$GL}ZjY0qkfAPNYlSpy;ED~Ef+gB-_$m~#-Cf(>qC"
    b"lU?;kN&^c7Z!$CHLqEV8YA7HC1mYKm{}e_j``DN4nIKmm<kEZ+a$&o_Ly#BaMX^NcPYz)pYvUH`R+g`6`+M^fv=1#$zww*#6LalZ"
    b"^M&{cZjGkb-C<7n&Sl;Nc`TV^1#!qKxV<@C<<ste;{rqm?k#?Yf16Np@&xgiB8v<I85Jw_Y^e@L;nup@_inqt*JrKUX~L4X-_GnA"
    b"Y!MpZy%CLyb14TUugvftvn$GP4|YQX%iG9iJP2#Jtu(zP^p!zL%_!aLX&G-;YUlGg+TTWt;uT_<|Er+1DKoQb0^};PY!s>z<SEHC"
    b")y;krUva*L(A8NGSVR5ofZRFTj6TnthfTf>Y#v&)FPGm50u2;xsy}GhU5c-tUq}C4n_#A&Ex(B0_N^XuskA(^NUqg~_Hz^DmqC&a"
    b"75uT97o3U(>v+Kl^0%W>yuni#>R-Z-hfRk1f9E@Yb|8T1w3&bsg2M?-{yyG`0(3xZuK$3^atNf_bc4Sfb51urITzV!g`ga&7wOnm"
    b"WBoypO^hIcm<>-%#?W~g%&H661*QVHapN}|_XUAZ&!}$(Uxwj{ACcixfmN&Ok9Z$yTqFhxM3@-1vSos$+dDt-fY_Mc_|DvEz6=O8"
    b"HQuELPr2GR(ci4`w`*X|=*?;FPXH;bCkSM!LxkfVJOthv`W{NscoT*aMek&UNA-dleXwMHLF1h;l&Hb+*`Gii3+TED3DEzxP^19("
    b"B;AvT7A^F*WBcF>+h}+)2g3Vr!F^Z69@&6r#YAd$^x2Vq>_k7yLFg})m(Ywd9on85Wz&2*umZ#^_z1g?{17egKo7vAhjzDR8yQ&>"
    b"L*f>X@*x_RV+Bw|5mr}()fG9hx+PTIR8Fs<eDYU`xQtpI5!8@hI9+A(@~@EWDgdt8z_Dhchzg_UI@}UfmP2M|St-^r1INKNbTfm7"
    b"sKke8Hc}04;6ij+sl5Jk!dE8QAfJwO)4A;)>UFe>FyB%r?7EY=bga;bYn)bAgvPj&8Xe;9Bfe`Da?5m<x%|xo9@=i6S&D6&jcb2V"
    b"&2h*%n#t;KH^Gz*zRG{)Z4=w#>{T_xvaI5n4r`pzD*u5&vRNhL3HUZq@||SWMvKqn^}wRACc&};2k_mA;T1SrAhP)bIFITow76|&"
    b"mscfFEZ&l4Wg?sTITX_W1{pTY=R2)!Y(vQC5uP+dO;AlZ=|4%^L{>ZyZ{{d+K8XxhteZppEkVvpK%u2ACO(5i9vyO46RZNgM(QQI"
    b"%P9v5Q8<OqcH*gzt6y!G=Y9%+R6$3q;@!#&j#8Moah-#z7ncJ8!1@8QS*1de73fH)MBHbhc}=H$IW-Gqf+Uw+{=r{@!6@-q!FSh%"
    b"@O?6b?{sPP2O;}Yz@rLBC0mbt_$={0sraOP;4HB^$=NHvil5b@v~!dEANW~pl!~^7_e4f%$HQqZVYUo=DOxFX$-{p^>NKHExDO%;"
    b"=_dPfOx<=K#+ma}iTqr2hkbyto?yT>V3+5dBcTJN#q;v{ND15O4_I-Jv~*O~BY@76l6{k`Ay|6>*19{X_pbNvGHQKS*X^P?%6B=l"
    b"9Yevo{;1a=-w8F?%j9z64me$2h$e_0RLXpp;ok`*PEuw)pPm(gbn1(2c82>y{%iDKjE2;4^2M2<(GH`~up8~8v3xp$`!QWG(FMGk"
    b"kjb_owdgH^rhC+E0my}4CWepeaANSNU9u)A9JCm-FGvTmrP$<e5gm}8C{vUY`^a!YwP`3x?cD%_1IjB+FH!7KQs#+DdB2DRoujb`"
    b"bJXH==xvFP>UI8ICc#kuC8;S0iO>EHvCK~Pw|QkBQpWW9=5S5ELU~T4;2)}ZU4@aLCzZOeD6CJO%S*GnWFxP*4=;_#UnGQ19@b(B"
    b"LZ}3<gAim&44p{k4<!lSD?IAJGSNY8?c)}5?3m6avrk|`xiuX5ZcOB6j7*bJ(L?`4-pxR)@^$J66S@d5iHy&Y3(y1Y>=Heo>~uTJ"
    b"hl!g^h%3ErXA1!Xavwl(Dad!ly4?p2Pd5_`dsSZx2H-Cuaw?G}vvzF@TO`yUtkScY6IqGKOp~<T+Sd5@p12?E2yb9Bo9GPsj7YKf"
    b"kIFZUj0Ig~!LBvs?02gn%*p!e&LG3`CA_Mk8w?_(SiNH9!B(A0*}sJLi)Sz1ex<qc9eD6nv=(r2rNU|CEC>qP*Y-~cqd$(rq|y#-"
    b"90ugf%Y(u31~rGr{Po~zsx7Adm?;V{!LDx#2F&uowu|)-@0&!0!AvCvGdaXyCd$8r{9O2L6;w^S3VI6!<ULCpBJUJf=V3S|$Z0N*"
    b"w})M^rz>9-OnVMif_pL9dG_@%(9RRIDfEIo&*es|?izRfLAN9ZwraeoN`N#G1VA^gV~K7`*;HI*gE+1&18B;lj~VTeV@7XYK)B5="
    b"mwyyKUi4<M6g*gTgbo(Hm*aur&p!ito+tR*1TJa+7fp8KpDhx7FUb_#2(+82aV44RwzPV6ZkDg{w*Z*UzRz-+-E&f5)D&Ia(uVSv"
    b"5szo8GN;25k(=Izskg0Z{&LzEz$0(mHa3@m+%rH()+tFUOn|9i+FgLCCL_M#p1Oo@L#6YW_dS=&<s-Cwq$e`;bWthx7QlcG;@{-)"
    b"{Ygp|6uR&Ty$nRWM`CL8;4ZMyBRV`OcKI<M&96|<jZn}eD9FbPQnp8<;Cnwh$dil$q6e0g*YK+kGw?_>4S_<LWqO&t%u%5>;+k{N"
    b"%CAjk09tNRpf$!pEAM(6H~J>w!9!FnklF;PPw>;Sz=E+@fFc25dWRg>y5zcSzPB-7rLoKNKO9r`I&~oBZ0BYz%VAP2kEPhqwiql;"
    b"3CqE>AMjql*NpAuZRf{76CV$8O4L&^QK9m6kYB`m1Rw}IO5|jk5sYo2{Z*nKlSjl?Ew}qSG%k5W8=8C4Ajl)SAXNTCDA3pM_K)4@"
    b"OY#F%Y5EhvljTd~SwW1<sQ-)M@k*THzET@@Z={b*!;@?A4EQg;Yaw;EH|dwjq+rO+lH7SaRo)bL-d(C+;s%W`;g|H5<SV1^3QXz?"
    b"r%A*#zGOGsp@E9<|IT2}k>M|Kb>$IU^87H&DSTVr|7mvrbtGlG<m<wbD_wFj@O3xsl7tf8ZuxRs0g1A>XgefYdSIDpuDrsRqEuq}"
    b"eETIx*3e3w0CnTJOuuA!@psyfdBgi2RF-$RJK_IKGt?sbbU+mXqBiGfzkR4h@R^5N)V@O2;_uaX#X6KhYIor7QBK`Cq`vK0@@K7~"
    b"jc2S4SD5~Hg8ha}4Q@~l_atC4)`Rsx*&6ANp%#r-Gklb_@qK4l`QhF=u4yDuVJ#?llPWjEZUgFjDT1+5<^pNH)VG{Asv(n`WdpMB"
    b"-Z26G=2vR{?PzVz?GI8&5JNg}SHp~p<rd8%M2=zi{{tx9xF7mFeprURul9W(FIvTM6#(c8B@EdMjH~298W|n1-XgXl;up#BKs~Ui"
    b"0C2SaHW)(3)yhp1H?yhyZ$rpo9Q7l}(oioE_JTJVVDKhj{hhd;!|?`nT+8d|Pl>9U_jcW%@o(1fO4h!*e9ekBLI`xiBpgWYymhKd"
    b"uRHG{)sD>xy^yZ0%vE|GpUjKplOIBTw|x=IClM68oUL4y=>ZT^A=Mt9%FWtvt4+zR_(J@E&LiD<!Jsd}ozlFbjp+%%gT6}%xRnH)"
    b"lYm>%hL+s6P4WO{Y^u=cOmbrhkTDH2dT>WB(WAy4Ig>{n+L3#7va<Z9#DG8e(a<?lxPGsbN>63_4>A<>wr(cm_h%^>^Um_%85%H^"
    b"61)xqRe03$zfQq&kqRe6Imn@Pl#^eny1E5-Yh#YHF5KQ!cV51#a)mqZZq<%bf3rE<T3CXX1(kb2f3>xAp7G423$=F7p8d5TI`y^x"
    b"J{aWZ!TWpA|4PK4eGdFT{yo35|BrwF`1g;0|M>ThfB*RRf8$@KMx&Yut`OXEaO+X!E&NMWk&$uLBjEpMa6bn3vJ$s1s8&4(?g?-^"
    b"!F>$Q3T`^MwcwV3GveMaxPdXXsu$dQ;NAqc58U(M{ux{&xGqT33@%fvQ9UkbRF&W^7d5J6aA%V=s$<|<!R-V047lCkHi5ef+<b61"
    b"fV%{o0Pgcdjj9J+JGh^N`#!h^a67@R2e%wt0k~VinZZp2H<kc(K)X(1+W>}3z<B|#TjAFV&IN80xSim3gL?wp_rd)b+-u<819uFZ"
    b"3~msd5#YZ8oE6;N;68=&e+a)XgF6832)Iwcjerv%&IIl%aM|GQ0Jj9(UEtP(s|EKAxP9Q>1otku6A8Qz#sFuRfG~C~xS8M<fm;P`"
    b"Gq_rCd%*n=+$-SP!F>Sk1h_$P8a3b-+B*inpM(1t+!1iC;C>G7``{YE)qrz@yBpjhaC5<BfHSH!Vfwjds#Wz4xMSenyV9!CPqV7#"
    b"!tVp%UIgb$wW@vyP7m>)UusoZuC}UHW?EI}F0rcqV6v(ngShX46Cm!tz%Qg(RX2k3f*=1~G1;ox0&YpVRrLnAKE)+m7KwlRve@{v"
    b"%Omljf6e@-P!s1L^9h1y^^w$HoK`gt-168n;w>tbdO~+9OH@6VX}y2NggC!3&Yv3RS6v$GSI7Bp`N>9g*R&5(pUzV4xvt>g)tb0?"
    b"ZJZw^(3tY#{F*qwHqI}^`4i&&iE(~M+S8N$uJ==4c@6Q=dV5k_ycp-75a&;h^QXl5b#Z=uoPT1R-w@|F#`#m@{H8d6TAY7UoPTnh"
    b"KRwQWSv>x)j_aRzza}nyoL>{?Pl)p;#`%-t{9>GcLYzN2&Yu$J*TwnuasG*MenXt!80Sxo^IsC@pB(4EG|q2|^QXo6C&l^G<NTM!"
    b"`7e)$C$9f4jq|H+itDd9zv||=_&EOq*IYNP;f3zhCq7lJ6)k^U=h#;Ip~DR08>Y7ZzWV?DSL)!#{hd+q56moG@ZOu<sZUPe{%%*("
    b"OTR;ZGWQ>e^M4)wx_%1hulpX2@K^js7vit@ojxTJj*jN?N3DO=;lG!l%<OBds(f(wf%_Twe*nL2%J-6M`R{-Q(&t)LMsQ|u+1FWB"
    b"_Uo;xt>E^7YrdYB*9_^p!1bcL71HIwFQnfC<#d5lLB8HQ;nxazvY^~Mxl`R>RXvA(NWTwU_8s7dGWJ3ET8KA7dNaf~Plq(%%urv~"
    b"^}HS9!BM*j>IC;3{$@jY?(x(0u7Nbg`Km5(W=N+3XT|jQL0WKoz;%IBRe&E{FaB->zX#&LS;4JE2YI%FtIdv{pH^7oaUQ})bXW)<"
    b"_#MK>S|v>kJ|NB7J0kda&U)d#jc$KeA%xlfdi#wFArH8&MG&?W>IP?A#?y5<;JXycT@G>Rw!rrafaPxZ2AAywe+lG=-?e2>K7_4>"
    b"Z?l4l{DOJ&ZG{Vp7A{)6q<HBvyhO6x=_<Qx#og=fxp(~r_k9%`J>S}N|K=@QAE?~s^=;p=^TCI*Z@D#R=B(RppFJn*=4d#x?}7T("
    b"L0jN=AGls{=6eBNa9h_y*am<Z`g<+-_kr63Y4?G%uZzXYTJW3Kj*pkGGk(5~d+s5Q$Lxop4sd($w+ia4hWf#oAL8}xfp23Cv<2MS"
    b"U62=?sut3Ls|D9p%hTZ*Tyemvx(8fxvPy+J<~QARlWMxXa>KT5=8_HG$_LHfE#~zb?(yAc_Eu~#uiLtH)5d$(c{gs^Y`)RFXyJ16"
    b"{l0Bp^F15P8#b@IXVV7M=nMkWmP+%+&F(Fg_w$tSf5ny^<_EX<D$QFfx7=5`?tb&V>o$Y)ZG$p5o7ZjIwxJS}CcD>d+~lj=FvGlU"
    b"!v?C+wQ-wo-6r$AtSs~TE%*BF->}&mE|h26rYhceZ{?P4Tio90)Fr;n-i`NfFfZA7PvyGG2N5pY&aK!m$UT=xY01XT8}O@e<0kse"
    b"4FR`#9c1)v{?_I#J2u~;QrUShWy%kMYDQ2utiMu))(YT%HL6b5CaMxOM!{yYCE&kV*(y6$WS&0TepiyHx;;C)%$@{(Gih=W*H)~B"
    b"e=611tvlhL2q{!aDp7<V5&lE3YC1^kKGi1pk5H?czS*~F6MR-G&D&5}3D{PtmM>XWTFQNT?8nlDOBY0WRr8k>=Pz6u2`RZP`_|d|"
    b"<Qt)x*m2m+8#izCZd|u%<3k(F6&u!V<@qq(?U-)!7B6)27T<jp=51To-MhgI{cGN|Wyi*-jMOuce79XN-!||1i{zVy`L+TXn741N"
    b"^kRp)eVgwkq~E)4(<VxY>1JNA{54xPZ`irfd-FOk{+PYk#Blky%!zIHmaQA0;4PcCZ2|xK4cj-~8<keU(T1H{H{9#pu%0jzjaN)_"
    b"dt93PeVe=+y%m)k)~yE&-TSTh^cTj9l4<=q?>b1XPhNM=W*kME!o$Y9q4NHXn`7~nJ?DbuZP*ML+_D)*4J603voDx-UFCf=ytak#"
    b"n|&*$b#K}N)os4dymiaQ&0fk1A?r7+SL#>j(1uOCGC4VVtnhyWcP`upq5ofd*8?6^b>&ZD)ELtmsDDt9j)hcI0^yGp0h_$}lVoI)"
    b"3^NlFQmnkpyd+~LGvk{XNT@~r)!M2E7M1N<1x56;w9+oNtjh|u=)x`nR;zqi6%|{$R2xJQMV3A1-uq@=GN88o_S=5_&M)7|x%a$t"
    b"&pr3=yZ602GhrNg3A4t~)7Y>y!C+Q+b($y8;PFiuZ{LR*S5#KgdyQHn?bB0f4V!+B;ZGzpNg<Q*=4d>Um<#o2R_`#Ji5?AbHZdoR"
    b"9}|hiq#d8@`jEHYL%gA>-V^Y;gsi@?!4uK~Gb!u}&GdVeuB*}K(?T8*)_gu3_qwTfWOOliG?^I@bampWr@17Y(IW{HG_wN>f=xn4"
    b"A`CM_x~@bl(cKm$5zH{+#=MLXqli0!Z5O4PFJL4yZ8($SI89{Ioer(tM7cOtq2uI(Az!A)=x)OqvxDrV(z+ucG=g)Z>3N13)8i4S"
    b"&0zn=-a!dnm@Y!slX^Uw>crW(J`pj@xFeV_sh%~Qr%fDdr0a=y#85}dP*RJXN{<6LjaWxC(~Wi76AdS_w!o>UZp;{zw-GVol9SvU"
    b"HiRFFQ*ofi)Z<};xDgL`(%c#sI>?1Bv>A<q-OrGzN21iBv71Y0GdM38kqRty+DJh*-i5s|lIR9Nr{mEGj+3wA@NLsO&{arLJyvuj"
    b"aQvvSo~=_6ci65uY}aCmIeHgP!5N&^6BQ;EJZV;hJ7tq%*pUs#=OGz$E9M!xC{t%5-ho-hJLsKcA|_-Vm<iqx&1hPd)4;kWd3c^d"
    b")d7|<O9SsT!j(*l2+NATq~=CbRPL0l=Zbb!hbdWS6?1HT%93SN|Fq(=JPuKwtW5RKY~0qrb28cgtT^>op=HzQ7Cp-rr~ZN+$ckgV"
    b"L^7tHvfJ&j^;Jt|#2hI-Hb;!3tW1q7D;~*?88bU(tZQL0E@VsQWVx}Im8mgn#oH3G=p0nB;<{}NC$R@&P2%)af$N5OQ5-RG(e?>*"
    b"uF-*!ig+)EQ(gUJZHX={TR%MvV+&LA3adS%rYNBreE=O|++{CY@tAGsXJyfFXWEFT(gyY!CDY~bjYGQ_YdJeA-p`Jbg=w0wrD>xf"
    b"PtGc@DySdk!ZvwVE}R{Iy}9vcT^l&QEIExGD|`d?FuH8Tqo$D!V{ePLwHbQcmX`XK6-I|~fs(t1m5>X|u_W3nl1bZ(C&nE$YC1RD"
    b"WMwIwSafW7!={&tcH>gFJ!(X9G8*q{xLY#fNS%<aSQ^_ZSKXR(QEK^SYyPavaS|DY$BmfYpfwQpHq?ORZoz{>UN^bBdonh81TorC"
    b"k8n_+7XkHSBV&<)zaHm)B)1X9&S02iw;?en8*U6^6JjuEB-55q!vT=OdHC8)Ow0|};@U>+yOL&<I(fZrin*-DXfrcvZGEjC7eUO2"
    b"?2}!xNw&xi*}!zYWP{RET1o>!S`S3z98_aQMJUvnF;hy`Y(%i0Wh9i5p?aKOND#~@uBRz2r6YaPBOSUf)&a;dic-9YI;cu1gwN;("
    b"dV@}(Z|EX=iVmaS=suQ$3Pbs}LjH4rMhz=c`^<gt0>1{UkhUO|P1j&H(r%>c0LlZJ&~GBN6loS86Q;Wy?#0@Kn=mHa9TD8<5$!N$"
    b">@29d9Pc?Fqn(W!&@spY+xm$<#Y1NytvK!TUfQm~Tidm4ocQMdlJV~%Ux7sODLXaLcINb+#PBma`=|TEE*XCk`IcQ;RvzCi<r?x@"
    b"q?URo*nP0VlRnn^J$EPH{R3o_wnfRPEc8r%6~;+-{QzCdwmlEaF3~o-KH6Q6dMjsYS-VG--Qr_^nO(=R{&wkr-}$q0cKyes-PwPk"
    b"-JSt<H=y2|v!yLib!w$88j$|h0eL-&@z^K1-qClW048E@={ug24Jj;yjc*jdB%5BE9zvsDi%qr_We$}2ZL*yx8`7`$@q0slZ}_*r"
    b"H++e9dajI#%an9T?25fO2mY|Ymk8@I+*}y2N`{-_w8e(|WXwn5dt_LP;T3>~DApA)aAjiB&gAQbL0my3+H;b-QA3a9;@_j)N;a;+"
    b"4{0}J<gU*z@Wyc?PWc)UZ#--o-C{HQExR1=9hQ8)u;+>;aJ}#fmCGGXb&<&+ZN4>_UVt*WpG~=OF@(2dvloZ)C!~wpxJ=BTM^p{C"
    b"HbChjVXY==rqU!u$?L+ViJRh3ZxRLH6&ejjk5X7B%BLQLq5euy9_zu_`II|t(6vZ}9*^br<Z>sy4A9-Aj>{>v*G3DTLfo~*Q!!lA"
    b"D<QynWGAb#p}>!;bJ=pabPI5O&@M|Va>RQdxM;_uw(}m`#XnULzy&m}bWK-GPo+@j`<Mz>Qi)!*=l>UBdwM2nWe2khyjXL3EYXq6"
    b">+u4=VRYr<cNf^76)YBY5~QVUhX$7v2CWtdVYQ+5bD|EVNQ29$Y{A|X?d(nHz}%E8P^bKtxqERJOzlTc4!Y6G@SI(A8Q_{+O9xO5"
    b"E*5pKQzyrn5;MRxm`H12@l)P-dje|`_v;a99;O#IB_r9|0tjG_n}aJ%k_m&bryyvcdaT2Xrm}_KE2O!)m?KK>4JYCnj8<h6`dA-f"
    b"^z#yMb?Rn=sEUyy>^F@$8eAd5O-bBIQriVR0jrmcp;l{58u4jHFSX)Oip#1|k_&`{1_26SIK|vX%n;W#7(sDQJkzbTHTMk7@3pK~"
    b"t6C1?&Mo3JGqhH&0hzq9?FLbDKbA4=?2=6cCdH^NRlL@18FMw(yF%IC{l4{-Nj$*9xi2^7>Tu63#@8rOLunm%hDq5bkBQkS(T&@%"
    b"2t7sCz(+bWu+ea90ni1Wo@iP<^@0ni7l@&l#`<l`qz&rT2gpXAbZtRBuFmDSeMscur!3(|;>nlG4{#Rc)aa?FaA!fCp(o`;S5p{L"
    b"4+jk^V|c+fi(0}PMVf#iQ<)+b6nm<;2#d)T{Dn>NPEi37Pfr*(2UsrjDoq=Nd&K<V$vs<?!wB8~aX~#j`*ilEjZmUF8ZoH5z`du?"
    b"Z-zI>zx)gE*2(3~=wqQ}Hk8Qb1w*NZWqY|28Jcr1mu(i2LV!P8wM|nb_*CC<nYb6kTSd?ikC$OuVJMbDQ#14!?jh<ZrtTtQB-{GQ"
    b"wREl4(u|3kQ?nG@AY!t|0(`S@hJ1=GD)#MyKpO8^b8!H}w+fpvf6>^`izC^3{65gD7MuZSIvgN|I}3b<J||BdhJYAms_5g?*pYqe"
    b"#rz(DH`bSM^yv}d2;5QNbJb&)P*Wo;wa2jqu8=iLF?qYevENUEI^VF$tZMH<YXtb|Au{!$%Sd8tpQTU}!(mN2&P;nd4kUmw(!t5E"
    b"v0ZvL9B{}bakk9*_T~N(%z2PZlkGV(bTdj1`ZYKrMmjAF3^|CQj{FWqyN%XFT*%Z5D}WFC>!RHT)njBW_K0^zlr)r(QzwN1=Gx?P"
    b"rJ|y6dG<b$yT8AVwcd@R-7b6H);@N5pXk4tSj?}dJJm{{l*)P%-R%VdJ(@DI;}&4>DQcw|zD8G0In)>9oz6*1BR%3zW2@aF<D%P="
    b"V1bOg5)lz)Fc=I5gYgfA2QI3HRpYB+Su%GfElKC)mRCdH?%XrSvb(CG^6i{X+4EYStv~~=IWo8f!IcQTF79onrwj6Zgcfksd1rXQ"
    b"i5nSuvw%yFSc8$Cn=re?yRBfNJv~<!uWA5yOliApmR)(4yn51Wn5F{%&7!mE5rFw-JVg$Xt%`^=T9Hho(n(wwnnqh9k;XX6!tLVS"
    b"PoQ3ti#cyRm6or&p*&R{E=QYaNccva-W2%*jqWB_2pkmvzClhf<3@Kf-CHT1<D2t@|6x6TY1$DMCLQg#Vsw<J=y1i{Hh`X<ba%3+"
    b"XAJ&_U`Pvu9Jqh=2Ry-`x3R&|B#!xbaX;&ImOzc3)?@Op$z(@AqasgXn(SuKYpU#K-HhX^d9szKqf<{=$DSN%T*;TvQ6&kGXAICJ"
    b"y_QGi(T-GCG?~Qo;v9(DOVB|P%NiXj3FGoyow+Je>BVsyyAC}f!gT!&nppNgYsi5+sfb}ZqA5pIKItd{yB$$cV`Tkf3*f$Q%;j01"
    b"5tC74RC&bFhP%YnWvDwsWSvsiBEt8HUvk1Iq+v*9NJU6T2Rp$Xx?VnRp|cyI>uJAFi)jjb;^ClsnkA1I^w5OD{#d3X8c&IELn7@q"
    b"+Cls@G)%_M7V^}K<6vXZVYkm`J4++$8FzVRuS0B+sBX%W=pBv}RMo;%xwP~b?~AfWmngL(W}R>&n|h3@vscuPcn=zj(QbjbPDaLr"
    b"lcJvod%N2bG2ucx?wG~<rSjB-@#T^7h;@P{cV_a`=PJcn%)fS0DJVRx==3wrEI!M6VNm|nOGkZ*e#zOTU-;rVWrGHP>D=?qzhKCP"
    b"7Y!YD@$fG@F8Ruczl%AN-pO1}f!KfEYL{1@=Y*+9^28KkUA6dCj?7A&Cy>@JmFI7X2-Q(nmKWGxt(4{GS*YIooC<}C7>v(7ERoK)"
    b"^_|lcr+1A*km&afzaY=O0u9|Wk?4Dnixodh@e+0IY}>W-Ra)ZbD7$4!MqdXsSP{uDQSvKQTvKtEiu+ZXfRYClZ&vnas=Q-LPA}Ez"
    b"Mn)6hFuKPmU(Znb3zW|b6<?&TFILx=C_BrM=rr#AD!y9zvqt6jh?4(O`L|PDe_350a;B_{foF*)i`%NYHIBx4J#L6w)SnJ&Z~$rl"
    b"K}}7YMdJMM8f=)^i+UGbqS|fk>yod2Sn`Dr>=R$NR6T!z;E$sIuO8a_kmD5XzVLq}uU7nt&#A8|{tMLK_2B*oFM_upJn-N*PHlhw"
    b"Y7v@_9clXBZ|-%#^?PsFJ3e3kg*~tB`v_p%d@H5I?eA!C6A~uha<-CPjA83t_&v7p9T+ZF;ib0lowo2YTX?xGe3vc!16%ks)vtS0"
    b"KN0WZOFsMFKpowFF2g=YzyD`VjFD}~sn6YqoJ{s0r}5!KPJL+@avC2;-__`2gs=lSjmZ_r$#4ugef!}=<n%K-pI|*vUw`o(P58SN"
    b"Ii021fP5bHA>`CK>hS(V2MSiaBm3C;pz~A9vv0ulqXXjGJ|q4AB^-malah75V(&1gAes#Z{*B81IX=f<9k$J<{Vh4kUw@5-w!ebU"
    b"`DahR$o5zGIsdG*4!+fi{xC*ymvu&_PmTfq6*%W&_`q<d2=7thWur9Mp~CyhHQ1uUt43(BQH3jqX<2*!-}rm+qt4+JG+WUL1^PLe"
    b"L);Y^3<iV2U@#aA27|$1Fc=I5gTY`h7z_r3!T5&&oedCQB~k=X@X3i2bncJNcU2>uI8C0<TX^Ec2|DjYXQdoSHzUP9)WFlw1TBiY"
    b"6`v%y29?Mgd`=iC;x2F?Z>_6?VS;<%T;#60Ab^tp>4=Q)IU=ub74Z;kI3n$=IwI|_I3n#Y5!?qoN2L9T;7(`}+zWMrUkg(OZ-tS9"
    b"2ccN-5Pb3h@mlEnK-%4}_>0JE0#4W}xC_<`?t@i=2Vog<w?~7U1b0EF;67*(JP36k$owZE_lANn8hJxw0EQ@DBzOb->3t3SAt&rX"
    b"?g<8Ao8V5^D7X*S2;K<G1b0DNa5qE*uK~Z{9+)b4EsPSp4u%L`55<Bv!25@Zdttxe8tfLl6}AW-fOUd5!F__ygj)rl0X@irGio4t"
    b"Se7exSk_nPVOdWR#b+UJLc1a4wax(e4pX}|fSY(L`lsZh6(4z++S3g~kk?JCg;I*Q`k+|xPu`R1`xM`g+#m45@7^PSroj&6ty&Fi"
    b"K|T%ZbG?eMQSoKSL!n0DFXgx3J;{^rNk2Q4zon%Ym7ZDlwW8AEilWnsO3TWMFBV4)OK==iPOKE)qZWFP>cS5`#V1`UK0*TH#$PE8"
    b"PM$4w+bHZtof>ZgOjUfKZmHB2-)%LKbOIWTR(zoDIZ~HC#sCh~@nU}%qWD1Fi-qnu@mYd0QAZvqCf@AH)2$G?<Ap9znVP1bvTP+-"
    b"8<mq}JsdqG`&1wDdQVG!*`%(mY)&|Ux=v5Nzh{=BZn*L)3hz54$I>3;T2m-b_bjP<HHCK{lH-1>&<*DMD|Lmx>ki4jf2y*TN?n`3"
    b"E?9$UTv~p+m6Tz)(q0d>uo8J~s6OAW)V0|S!tG?YF25~G&c*OVyImJ7AYJV1d3L3)&8`p9sOxLWZ;KL~sK@ndHw|LQ{U<5gS;H{g"
    b"uYQ9t>yR8z6DM5N->%fP*>yu5wO?a?J(S>0Vtl_kn*mdi&+we2en+Bizj|ndN~(v({Jv8%3U&LHEdZmaY@R^A?r7BQ=Wh^(QQryF"
    b"=Idf~LO*|N;9TOarhMIrsN2t9AC!tVK8e4RP`97IGoc81Q($Jk?o`z6=Wi<<?W4IbUzf1)s0JI5)+4P$dK765(ki5tNXw9JMY;(o"
    b"iPVWS3#kPugycu^A=M$dk*blVB27Y?h*XI*8fhfb5Tr7sVx<pANAbShhqNE*cSyUDwjymo+Jv+LX%*5+BuAZ7oc9#{48z4upG`L_"
    b"?5UGyninMHdC|T@@;li4!O-8d?(w_-w)76K6J~pzdEX~DFrJ51h1J>cw$pRrkBhV6>ibHwVgIks$%aS1KiCQ{xM$`0R@kxWDfOc|"
    b"MVq$|T{@A%tKZqNbLi7AG*mnK?tdbA#iKuY=10-$-Pav2fBT}PjTatVTz%s`FW>F@;^}u>_W1qPA8lUcerMs}I~Okc*Xqqvf4g?q"
    b"3GbJCo_?V^@$A0a|F~d#?UO%vRNM5OuBJ<`zT?B>zMGtzUS0ayM?X4taQ<V{U8{dT=dB&@T{d>f!mqkVm0j@I(Vv#R^~~0f-3K3e"
    b"@$iQS-?(<(-Mc)-j{jKx#kD_Ob>UkN)qKIYpft1amdu>(b@eUI{g3?M>M2)l{P{b<`bXZr?wV(=n{wOzceS3lZf)Oc$Cl8;w_l|{"
    b"fBd%A+xC=S_q~r^>3Hn!qlYiu{NT3hUR@CPZU5(c9p5hu%-&iqzF+sb9nZ-hcHD8S>c(qIUVbP^|BhC*My9;pc*ni*!HYkr`t=K="
    b"jSJswx!{-2AFA4Y&WI(oLu=PP^T@kZ)oXtdjXi$)zh8CB!Kw+@Y;w+f`?o7Lzx0Qyr;i`ssV^BccgK(SSB>?3<Bj^QPp!E7_uH%P"
    b"+8UgaaX)wNQ$KvX>a~t1S6uD+$?%`;T2VD}#ItX1dUDD*{kC~kdeh8b&Hq{OrosPqebvkFj=kfIr|$aBdB@yUBdZ?%<JAve`rkJ{"
    b"dU@5i*R9^aDRNWI?pK?>9{$!DJ4S@&E<Uk*;Wf)Yo_yiFaJg&TmUUAv`QG!B7S-On5stq+<#)HX6c7E`fwyj1d)ky|mw23K{^Fl9"
    b"SG_W3@`M|Q{bs}~<KOizYrT5ycc0qQy!YWnYae`K{F|LWAM{Az0r$*bmW?j=?yvaT#Kz!HcXpNEIkRZZme-#C_OS!c4!{2ox3)Gf"
    b"pSsz<_$xyirWtL=7vK5#87sa$Xn)0P5A6KSwxU<p?kTbQ^>E}<km##9>2nSDB0YihBGO?b`put8qz0t!g4}qZbdy1THfS!0&x*hX"
    b"pl?dTWeBZXP<Jd+JyJ}iyYC};9(+t4eRp;^5iuf;jQFT)jZWWFW_<#aoO3qSPIj0^Dy+vyA!f9v9pw>6Izb=JZ8wb@Ge$hzThiZd"
    b"l{SMuZhJlbXhL;0(9e%AvwfyIxl7~CA%nqSFc=I5gTY`h7z_r3!C){L3<iV2U@#aA27|$1Fc=I5gTY`h7z_r3!C){L3<iV2U@#aA"
    b"27|$1Fc=I5gTY`h7z_r3!C){L3<iV2U@#aA27|$1Fc=I5gTY`h7z_r3!C){L3<iV2U@#aA27|$1Fc=I5gTY`h7z_r3!C){L3<iV2"
    b"U@#aA27|$1Fc=I5gTY`h7!1az;C})7+j!U"
)
CODEC_SHA256 = "13f2e9d6f2e27aeb63951ad4d7c5b468858bf719d619fd14e983baa9802b7e6a"
IMAGE_BASE = 0x400000
CODEC_ENTRY = 0x415820
MALLOC_ENTRY = 0x40AAE0
FREE_ENTRY = 0x40AF40


class FormatError(Exception):
    """The input is not a complete, supported RNSetup file."""


def u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def checked(data: bytes, offset: int, size: int, what: str) -> bytes:
    if offset < 0 or size < 0 or offset + size > len(data):
        raise FormatError(f"truncated {what}")
    return data[offset : offset + size]


class PEImage:
    def __init__(self, data: bytes):
        self.data = data
        if checked(data, 0, 2, "DOS header") != b"MZ":
            raise FormatError("not a DOS/PE executable")
        pe = u32(checked(data, 0, 0x40, "DOS header"), 0x3C)
        if checked(data, pe, 4, "PE signature") != b"PE\0\0":
            raise FormatError("missing PE signature")
        coff = checked(data, pe + 4, 20, "COFF header")
        if u16(coff, 0) != 0x14C:
            raise FormatError("RNSetup requires an i386 PE image")
        nsections = u16(coff, 2)
        opt_size = u16(coff, 16)
        opt = checked(data, pe + 24, opt_size, "PE optional header")
        if len(opt) < 120 or u16(opt, 0) != 0x10B:
            raise FormatError("RNSetup requires a PE32 optional header")
        self.image_base = u32(opt, 28)
        self.size_of_image = u32(opt, 56)
        self.size_of_headers = u32(opt, 60)
        if u32(opt, 92) < 3:
            raise FormatError("PE image has no resource directory")
        self.resource_rva = u32(opt, 112)
        self.resource_size = u32(opt, 116)
        table = pe + 24 + opt_size
        self.sections = []
        for index in range(nsections):
            raw = checked(data, table + index * 40, 40, "section table")
            name = raw[:8].rstrip(b"\0").decode("ascii", "replace")
            virtual_size, rva, raw_size, raw_offset = struct.unpack_from("<IIII", raw, 8)
            self.sections.append(
                {"name": name, "rva": rva, "virtual_size": virtual_size,
                 "raw_size": raw_size, "raw_offset": raw_offset,
                 "physical_size": max(0, min(raw_size, len(data) - raw_offset))}
            )

    def rva_to_offset(self, rva: int, size: int = 1) -> int:
        if rva < self.size_of_headers and rva + size <= self.size_of_headers:
            checked(self.data, rva, size, "header RVA")
            return rva
        for section in self.sections:
            start = section["rva"]
            available = section["raw_size"]
            if start <= rva and rva + size <= start + available:
                offset = section["raw_offset"] + rva - start
                checked(self.data, offset, size, "section RVA")
                return offset
        raise FormatError(f"RVA 0x{rva:x} is not backed by file data")

    def archive_resource(self) -> tuple[bytes, dict]:
        # The resource directory itself must be present, but the section and
        # archive body are allowed to end at physical EOF for partial recovery.
        base = self.rva_to_offset(self.resource_rva, 1)

        def resource_name(value: int):
            if not value & 0x80000000:
                return value
            relative = value & 0x7FFFFFFF
            length = u16(checked(self.data, base + relative, 2, "resource name"), 0)
            raw = checked(self.data, base + relative + 2, length * 2, "resource name")
            try:
                return raw.decode("utf-16le")
            except UnicodeDecodeError as exc:
                raise FormatError("invalid UTF-16 resource name") from exc

        def entries(relative: int):
            header = checked(self.data, base + relative, 16, "resource directory")
            count = u16(header, 12) + u16(header, 14)
            for index in range(count):
                entry = checked(self.data, base + relative + 16 + index * 8, 8,
                                "resource entry")
                yield resource_name(u32(entry, 0)), u32(entry, 4)

        leaves = []
        for type_name, type_child in entries(0):
            if not type_child & 0x80000000:
                raise FormatError("resource type points directly to data")
            for item_name, item_child in entries(type_child & 0x7FFFFFFF):
                if not item_child & 0x80000000:
                    raise FormatError("resource item points directly to data")
                for language, leaf in entries(item_child & 0x7FFFFFFF):
                    if leaf & 0x80000000:
                        raise FormatError("resource language points to a directory")
                    if type_name == "BINARY" and item_name == "ARCHIVE":
                        leaves.append((language, leaf))
        if len(leaves) != 1:
            raise FormatError(f"expected exactly one BINARY/ARCHIVE resource, found {len(leaves)}")
        language, leaf = leaves[0]
        desc = checked(self.data, base + leaf, 16, "resource data entry")
        rva, size, codepage, reserved = struct.unpack_from("<IIII", desc)
        if reserved != 0:
            raise FormatError("nonzero reserved field in archive resource")
        offset = self.rva_to_offset(rva, 1)
        section_available = None
        for section in self.sections:
            if section["rva"] <= rva < section["rva"] + section["raw_size"]:
                within = rva - section["rva"]
                section_available = max(0, section["physical_size"] - within)
                break
        if section_available is None:
            raise FormatError("archive RVA is not inside a section")
        available = min(size, section_available, len(self.data) - offset)
        if available <= 0:
            raise FormatError("archive resource has no physical bytes")
        return self.data[offset : offset + available], {
            "file_offset": offset, "size": size, "available_size": available,
            "truncated": available < size, "rva": rva,
            "language": language, "codepage": codepage,
        }


def parse_rzt(archive: bytes):
    if checked(archive, 0, 4, "RZT header") != b".rzt":
        raise FormatError("archive resource does not start with .rzt")
    if checked(archive, 4, 2, "RZT flags") != b"\0\0":
        raise FormatError("unsupported RZT flags/version")
    table_size = int.from_bytes(checked(archive, 6, 2, "RZT table size"), "big")
    count = int.from_bytes(checked(archive, 8, 4, "RZT file count"), "big")
    if count == 0 or count > 1_000_000:
        raise FormatError("invalid RZT file count")
    table_end = 8 + table_size
    if table_end < 12 or table_end > len(archive):
        raise FormatError("invalid RZT table length")
    offset = 12
    files = []
    for _ in range(count):
        length = checked(archive, offset, 1, "RZT name length")[0]
        offset += 1
        if length == 0:
            raise FormatError("empty RZT filename")
        raw_name = checked(archive, offset, length, "RZT filename")
        offset += length
        try:
            name = raw_name.decode("cp1252")
        except UnicodeDecodeError as exc:
            raise FormatError("invalid RZT filename encoding") from exc
        size = int.from_bytes(checked(archive, offset, 4, "RZT file size"), "big")
        offset += 4
        files.append({"name": name, "size": size})
    if offset != table_end:
        raise FormatError("RZT table length does not match its entries")
    preview_size = int.from_bytes(checked(archive, offset, 4, "manifest length"), "big")
    offset += 4
    preview = checked(archive, offset, preview_size, "manifest preview")
    offset += preview_size
    if b"\0" in preview:
        raise FormatError("invalid manifest preview")
    return files, preview, archive[offset:], offset


def decode_zlib(payload: bytes, allow_truncated: bool) -> tuple[bytes, bool, str | None]:
    decoder = zlib.decompressobj()
    out = bytearray()
    try:
        for offset in range(0, len(payload), 65536):
            out.extend(decoder.decompress(payload[offset : offset + 65536]))
        out.extend(decoder.flush())
    except zlib.error as exc:
        if allow_truncated:
            return bytes(out), False, f"physical EOF interrupted zlib stream ({exc})"
        raise FormatError(f"damaged zlib solid stream: {exc}") from exc
    if not decoder.eof:
        if allow_truncated:
            return bytes(out), False, "physical EOF interrupted zlib stream"
        raise FormatError("truncated zlib solid stream")
    if decoder.unused_data or decoder.unconsumed_tail:
        raise FormatError("bytes remain after the zlib solid stream")
    return bytes(out), True, None


def codec_image() -> bytes:
    try:
        image = zlib.decompress(base64.b85decode(CODEC_B85))
    except Exception as exc:
        raise FormatError("embedded Faster decoder is damaged") from exc
    if hashlib.sha256(image).hexdigest() != CODEC_SHA256 or len(image) != 0x30000:
        raise FormatError("embedded Faster decoder failed its integrity check")
    return image


def decode_faster(payload: bytes, maximum_output: int,
                  allow_truncated: bool) -> tuple[bytes, bool, str | None]:
    try:
        from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE, UcError
        from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EIP, UC_X86_REG_ESP
    except ImportError as exc:
        raise FormatError("the Python 'unicorn' package is required for Faster streams") from exc

    uc = Uc(UC_ARCH_X86, UC_MODE_32)
    uc.mem_map(0, 0x1000)
    uc.mem_map(IMAGE_BASE, 0x30000)
    uc.mem_write(IMAGE_BASE, codec_image())
    stack = 0x70000000
    heap = 0x50000000
    sentinel = 0x60000000
    input_callback = sentinel + 0x1000
    output_callback = sentinel + 0x1100
    uc.mem_map(stack, 0x200000)
    uc.mem_map(heap, 0x10000000)
    uc.mem_map(sentinel, 0x2000)
    heap_next = heap
    input_pos = 0
    output = bytearray()

    def read32(address: int) -> int:
        return struct.unpack("<I", bytes(uc.mem_read(address, 4)))[0]

    def return_from_hook(value: int):
        esp = uc.reg_read(UC_X86_REG_ESP)
        address = read32(esp)
        uc.reg_write(UC_X86_REG_EAX, value & 0xFFFFFFFF)
        uc.reg_write(UC_X86_REG_ESP, esp + 4)
        uc.reg_write(UC_X86_REG_EIP, address)

    def hook(emu, address, size, user_data):
        nonlocal heap_next, input_pos
        esp = emu.reg_read(UC_X86_REG_ESP)
        if address == MALLOC_ENTRY:
            amount = read32(esp + 4)
            if amount > 0x08000000 or heap_next + amount > heap + 0x10000000:
                raise FormatError("Faster stream requests excessive memory")
            result = heap_next
            heap_next = (heap_next + amount + 15) & ~15
            return_from_hook(result)
        elif address == FREE_ENTRY:
            return_from_hook(0)
        elif address == input_callback:
            destination, amount = read32(esp + 4), read32(esp + 8)
            chunk = payload[input_pos : input_pos + amount]
            if chunk:
                emu.mem_write(destination, chunk)
            input_pos += len(chunk)
            return_from_hook(len(chunk))
        elif address == output_callback:
            source, amount = read32(esp + 4), read32(esp + 8)
            if len(output) + amount > maximum_output:
                raise FormatError("Faster solid stream exceeds its declared maximum size")
            output.extend(emu.mem_read(source, amount))
            return_from_hook(0)

    for address in (MALLOC_ENTRY, FREE_ENTRY, input_callback, output_callback):
        uc.hook_add(UC_HOOK_CODE, hook, begin=address, end=address)

    def call(address: int, *args: int) -> int:
        esp = stack + 0x1FF000
        for value in reversed(args):
            esp -= 4
            uc.mem_write(esp, struct.pack("<I", value & 0xFFFFFFFF))
        esp -= 4
        uc.mem_write(esp, struct.pack("<I", sentinel))
        uc.reg_write(UC_X86_REG_ESP, esp)
        uc.reg_write(UC_X86_REG_EIP, address)
        try:
            uc.emu_start(address, sentinel)
        except UcError as exc:
            eip = uc.reg_read(UC_X86_REG_EIP)
            if allow_truncated and input_pos == len(payload):
                return None
            raise FormatError(
                f"damaged Faster stream at payload byte {input_pos} "
                f"(decoder EIP 0x{eip:08x}): {exc}"
            ) from exc
        return uc.reg_read(UC_X86_REG_EAX)

    streams = 0
    while payload[input_pos : input_pos + 3] == b"\xfeI\x06":
        streams += 1
        result = call(CODEC_ENTRY, input_callback, 0, output_callback, 0)
        if result is None:
            return bytes(output), False, "physical EOF interrupted Faster stream"
        if result != 0:
            if allow_truncated and input_pos == len(payload):
                return bytes(output), False, "physical EOF interrupted Faster stream"
            raise FormatError(f"Faster decoder returned error 0x{result:08x}")
    if streams == 0:
        raise FormatError("unsupported solid-stream compression")
    if input_pos != len(payload):
        if allow_truncated and payload[input_pos:] in (b"\xfe", b"\xfeI"):
            return bytes(output), False, "physical EOF interrupted Faster stream header"
        raise FormatError(f"{len(payload) - input_pos} bytes remain after Faster streams")
    return bytes(output), True, None


def octal_field(header: bytes, start: int, size: int, label: str) -> int:
    raw = header[start : start + size].strip(b" \0")
    if not raw:
        return 0
    if any(byte < 0x30 or byte > 0x37 for byte in raw):
        raise FormatError(f"invalid octal {label} in ustar record")
    return int(raw, 8)


def text_field(header: bytes, start: int, size: int, label: str) -> str:
    raw = header[start : start + size].split(b"\0", 1)[0]
    try:
        return raw.decode("cp1252")
    except UnicodeDecodeError as exc:
        raise FormatError(f"invalid {label} in ustar record") from exc


def safe_parts(path: str) -> tuple[str, ...]:
    path = path.replace("\\", "/")
    parts = tuple(part for part in path.split("/") if part)
    if not parts or path.startswith("/") or any(part in (".", "..") for part in parts):
        raise FormatError(f"unsafe archive path {path!r}")
    if ":" in parts[0]:
        raise FormatError(f"unsafe archive path {path!r}")
    return parts


def parse_solid(solid: bytes, table: list[dict], padded_bodies: bool,
                allow_partial: bool):
    offset = 0
    table_index = 0
    records = []
    directories = []
    paths = set()
    partial_reason = None
    while offset < len(solid):
        if len(solid) - offset < 512:
            if allow_partial:
                partial_reason = "decoded data ends inside a ustar header"
                break
            raise FormatError("truncated ustar record")
        header = solid[offset : offset + 512]
        offset += 512
        if header[257:263] != b"ustar\0" or header[263:265] != b"00":
            raise FormatError("invalid RNSetup ustar signature/version")
        stored_sum = octal_field(header, 148, 8, "checksum")
        name = text_field(header, 0, 100, "name")
        prefix = text_field(header, 345, 155, "prefix")
        size = octal_field(header, 124, 12, "size")
        actual_sum = sum(header[:148]) + 8 * 0x20 + sum(header[156:])
        # Directory markers are checksummed before RNSetup fills their prefix.
        if name == "rnempty0" and size == 0:
            actual_sum -= sum(header[345:500])
        if stored_sum != actual_sum:
            raise FormatError("ustar header checksum mismatch")
        mode = octal_field(header, 100, 8, "mode")
        mtime = octal_field(header, 136, 12, "mtime")
        if header[156:157] not in (b"0", b"\0"):
            raise FormatError("unsupported ustar record type")
        if name == "rnempty0" and size == 0:
            if not prefix:
                raise FormatError("directory marker has no prefix")
            directories.append(safe_parts(prefix))
            continue
        if table_index >= len(table):
            raise FormatError("solid stream has more files than the RZT table")
        expected = table[table_index]
        if name != expected["name"] or size != expected["size"]:
            raise FormatError(
                f"solid/table mismatch at file {table_index}: "
                f"{name!r}/{size} != {expected['name']!r}/{expected['size']}"
            )
        if len(solid) - offset < size:
            if allow_partial:
                partial_reason = f"decoded data ends inside file {name!r}"
                break
            raise FormatError("truncated ustar record body")
        body = solid[offset : offset + size]
        offset += size
        parts = safe_parts(f"{prefix}/{name}" if prefix else name)
        folded = tuple(part.casefold() for part in parts)
        if folded in paths:
            raise FormatError(f"duplicate output path {'/'.join(parts)!r}")
        paths.add(folded)
        records.append({"parts": parts, "data": body, "mode": mode, "mtime": mtime,
                        "header": header})
        table_index += 1
        if padded_bodies:
            padding_size = (-size) & 511
            if len(solid) - offset < padding_size:
                if allow_partial:
                    partial_reason = f"physical EOF interrupted padding after {name!r}"
                    break
                raise FormatError("truncated ustar body padding")
            padding = solid[offset : offset + padding_size]
            if any(padding):
                raise FormatError("nonzero ustar body padding")
            offset += padding_size
    complete = offset == len(solid) and table_index == len(table)
    if not complete and not allow_partial:
        raise FormatError("solid stream does not exactly cover the RZT table")
    if allow_partial and table_index < len(table) and partial_reason is None:
        partial_reason = "physical EOF ended before all RZT entries were decoded"
    return records, directories, complete, partial_reason


def analyze(input_path: Path):
    try:
        data = input_path.read_bytes()
    except OSError as exc:
        raise FormatError(f"cannot read input: {exc}") from exc
    pe = PEImage(data)
    archive, resource = pe.archive_resource()
    allow_partial = resource["truncated"]
    table, preview, payload, payload_offset = parse_rzt(archive)
    maximum = sum(item["size"] for item in table) + 512 * (len(table) + 257)
    is_zlib = (len(payload) >= 2 and payload[0] & 0x0F == 8 and
               payload[0] >> 4 <= 7 and int.from_bytes(payload[:2], "big") % 31 == 0)
    if is_zlib:
        compression = "zlib/DEFLATE"
        solid, decoder_complete, decoder_reason = decode_zlib(payload, allow_partial)
        padded_bodies = True
    elif payload.startswith(b"\xfeI\x06"):
        compression = "Faster 6/BWT+RLE"
        solid, decoder_complete, decoder_reason = decode_faster(
            payload, maximum, allow_partial
        )
        padded_bodies = False
    else:
        raise FormatError("unsupported RNSetup solid-stream compression")
    records, directories, solid_complete, solid_reason = parse_solid(
        solid, table, padded_bodies, allow_partial
    )
    complete = not resource["truncated"] and decoder_complete and solid_complete
    reasons = [reason for reason in (
        "physical file ends before the declared archive resource boundary"
        if resource["truncated"] else None,
        decoder_reason,
        solid_reason,
    ) if reason]
    metadata = {
        "format": "RNSetup RZT",
        "status": "complete" if complete else "partial",
        "partial_reason": "; ".join(dict.fromkeys(reasons)) if reasons else None,
        "input": input_path.name,
        "input_size": len(data),
        "input_sha256": hashlib.sha256(data).hexdigest(),
        "archive_resource": resource,
        "rzt_table_size": 8 + int.from_bytes(archive[6:8], "big"),
        "manifest_preview_size": len(preview),
        "payload_offset_in_resource": payload_offset,
        "compressed_payload_size": len(payload),
        "solid_size": len(solid),
        "compression": compression,
        "file_count": len(records),
        "declared_file_count": len(table),
        "unrecovered_file_count": len(table) - len(records),
        "directory_marker_count": len(directories),
        "installed_bytes": sum(len(record["data"]) for record in records),
        "files": [
            {"path": "/".join(record["parts"]), "size": len(record["data"]),
             "sha256": hashlib.sha256(record["data"]).hexdigest(),
             "mode": oct(record["mode"]), "mtime": record["mtime"]}
            for record in records
        ],
    }
    return records, directories, preview, metadata


def extract(input_path: Path, output_dir: Path, include_all: bool):
    records, directories, preview, metadata = analyze(input_path)
    parent = output_dir.parent if output_dir.parent != Path("") else Path(".")
    parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".rnsetup-stage-", dir=parent))
    try:
        for parts in directories:
            target = stage.joinpath(*parts)
            target.mkdir(parents=True, exist_ok=True)
            target.chmod(0o775)
        for record in records:
            target = stage.joinpath(*record["parts"])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(record["data"])
            executable = bool(record["mode"] & 0o111)
            target.chmod(0o775 if executable else 0o664)
        if include_all:
            extra = stage / ".rnsetup"
            extra.mkdir(parents=True, exist_ok=True)
            (extra / "manifest-preview.txt").write_bytes(preview)
            (extra / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            for path in extra.iterdir():
                path.chmod(0o664)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_dir.chmod(output_dir.stat().st_mode | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP)
        for source in sorted(stage.rglob("*"), key=lambda p: (not p.is_dir(), len(p.parts))):
            relative = source.relative_to(stage)
            destination = output_dir / relative
            if source.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
                destination.chmod(destination.stat().st_mode | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                os.replace(source, destination)
        return metadata
    finally:
        shutil.rmtree(stage, ignore_errors=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="rnSetup.py", usage="rnSetup.py [--all] <inputFile> <outputDir>",
        description="Extract files from a complete or physically truncated RNSetup executable.",
    )
    parser.add_argument("--all", action="store_true",
                        help="also emit .rnsetup manifest and JSON metadata")
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    args = parser.parse_args(argv)
    try:
        metadata = extract(args.inputFile, args.outputDir, args.all)
    except FormatError as exc:
        print(f"rnSetup.py: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"rnSetup.py: output error: {exc}", file=sys.stderr)
        return 1
    print(
        f"{'Partially extracted' if metadata['status'] == 'partial' else 'Extracted'} "
        f"{metadata['file_count']} of {metadata['declared_file_count']} files "
        f"({metadata['installed_bytes']} bytes) to {args.outputDir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
