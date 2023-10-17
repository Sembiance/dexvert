import {Format} from "../../Format.js";

export class atariUIMG extends Format
{
	name       = "Atari UIMG";
	ext        = [".bp1", ".bp2", ".bp4", ".bp6", ".bp8", ".c01", ".c02", ".c04", ".c06", ".c08", ".c16", ".c24", ".c32"];
	converters = ["recoil2png"];
}
