
const LOOP_CTL_ADD = 0x4C80;
const LOOP_CTL_REMOVE = 0x4C81;
const LOOP_CTL_GET_FREE = 0x4C82;
const LOOP_SET_FD = 0x4C00;
const LOOP_CLR_FD = 0x4C01;

function allocateLoopDev(filePath)
{
	const loopControl = fs.openSync("/dev/loop-control", "r+");
	const loopNum = ioctl(loopControl, LOOP_CTL_GET_FREE);
	fs.closeSync(loopControl);

	const loopDev = fs.openSync("/dev/loop" + loopNum);
	const fd = fs.openSync(filePath, "r");
	ioctl(loopDev, LOOP_SET_FD, fd);
	fs.closeSync(loopDev);
	fs.closeSync(fd);

	return loopNum;
}

function freeLoopDev(loopNum)
{
	const loopDev = fs.openSync("/dev/loop" + loopNum);
	ioctl(loopDev, LOOP_CLR_FD);
	fs.closeSync(loopDev);
}