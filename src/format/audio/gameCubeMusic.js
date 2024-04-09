import {xu} from "xu";
import {Format} from "../../Format.js";

export class gameCubeMusic extends Format
{
	name       = "GameCube Music";
	ext        = [".gcm"];
	magic      = ["GameCube Music (IDSP)"];
	converters = ["vgmstream", "zxtune123"];
}
