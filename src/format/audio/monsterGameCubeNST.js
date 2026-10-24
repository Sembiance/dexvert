import {Format} from "../../Format.js";

export class monsterGameCubeNST extends Format
{
	name             = "Monster GameCube NST Audio";
	ext              = [".dsp"];
	forbidExtMatch   = true;
	magic            = ["Monster GameCube NST (nst)", "vgmstream: nst_monster"];
	converters       = ["ffmpeg[format:nst][libre][outType:mp3]", "vgmstream[types:nst_monster]"];
}
