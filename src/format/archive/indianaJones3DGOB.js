import {Format} from "../../Format.js";

export class indianaJones3DGOB extends Format
{
	name           = "Indiana Jones 3D GOB Archive";
	ext            = [".gob"];
	forbidExtMatch = true;
	magic          = ["dragon: GOB "];
	converters     = ["dragonUnpacker[types:GOB]"];
}
