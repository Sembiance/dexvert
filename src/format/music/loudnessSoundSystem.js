import {Format} from "../../Format.js";

export class loudnessSoundSystem extends Format
{
	name         = "Loudness Sound System";
	website      = "https://www.vgmpf.com/Wiki/index.php/LDS";
	ext          = [".lds"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
	notes        = "According to the wiki, LDS isn't the most common extension, but rather .dat is. So I'd need to come up with some sort of magic check in order to properly identify and convert these";
}
