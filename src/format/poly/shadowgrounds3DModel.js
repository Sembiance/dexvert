import {Format} from "../../Format.js";

export class shadowgrounds3DModel extends Format
{
	name           = "Shadowgrounds 3D model";
	ext            = [".s3d"];
	forbidExtMatch = true;
	magic          = ["Shadowgrounds 3D model"];
	converters     = ["threeDObjectConverter"];
}
