import {Format} from "../../Format.js";

export class monsterBashTile extends Format
{
	name         = "Monster Bash Tile";
	website      = "https://moddingwiki.shikadi.net/wiki/Monster_Bash_Tileset_Format";
	ext          = [".tbg", ".tfg", ".tbn", ".pbg", ".pfg", ".pbn"];
	converters   = ["gametls[colCount:20][type:tls-bash-bg]", "gametls[colCount:20][type:tls-bash-fg]", "gametls[colCount:20][type:tls-bash-sprite]"];
}
