@echo off

if "%1"== "" (
	set DEFAULT_LABEL=coin
) else (
	set DEFAULT_LABEL=%1
)

REM set METHOD=-X GET
set METHOD=-X POST

REM set URL=http://localhost:9090/webhook
REM set REQUEST=--json {\"action\":\"PROJECT_UPDATED\",\"project\":{\"id\":7,\"label_config\":\"<View></View>\",\"my_data\":\"%DEFAULT_LABEL%\"}}

set URL=http://bazzite.local:9090/webhook
set REQUEST=--json {\"action\":\"START_TRAINING\",\"project\":{\"id\":7,\"label_config\":\"<View></View>\",\"my_data\":\"%DEFAULT_LABEL%\"}}

echo.
echo Command: 
echo curl %URL% %METHOD% %HEADER% %REQUEST%
echo.
echo Result:
curl %URL% %METHOD% %HEADER% %REQUEST%

REM pause
