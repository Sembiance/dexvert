import {Format} from "../../Format.js";

export class real3D extends Format
{
	name           = "Real 3D";
	ext            = [".real", ".obj"];
	forbidExtMatch = true;
	magic          = ["Real 3D ", "IFF data, REAL Real3D rendering"];
	unsupported    = true;
	notes          = "Realsoft 3D 4.5 for windows (https://archive.org/details/onyxdvd-14) was able to open 1 of my test files (Klingon), but promptly crashed when attempting to save as 3DS. Not aware of any other converter.";
}
