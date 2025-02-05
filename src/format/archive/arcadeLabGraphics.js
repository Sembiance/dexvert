import {Format} from "../../Format.js";

export class arcadeLabGraphics extends Format
{
	name           = "ArcadeLab/Retro64 Graphics";
	website        = "https://web.archive.org/web/20220705090053/https://wiki.xentax.com/index.php/Retro64_GFX";
	ext            = [".gfx"];
	forbidExtMatch = true;
	magic          = ["Retro64 / ArcadeLab game graphics data"];
	converters     = ["gameViewerLinux[plugin:arcade_lab]"];
}
