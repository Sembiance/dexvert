import {Format} from "../../Format.js";

export class real3D extends Format
{
	name           = "Real 3D";
	ext            = [".real", ".obj"];
	forbidExtMatch = true;
	magic          = ["Real 3D ", "IFF data, REAL Real3D rendering"];
	unsupported    = true;
	notes          = "Realsoft 3D may be able to view/render these. See linux version in: sandbox/app/realsoft3d-8.2.tar";
}
