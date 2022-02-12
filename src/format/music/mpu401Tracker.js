import {Format} from "../../Format.js";

export class mpu401Tracker extends Format
{
	name         = "MPU-401 Tracker";
	ext          = [".mtk"];
	magic        = ["MPU-401 Trakker", "MPU-401 trakker module"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
