@echo off
echo Welcome to Tic Tac Toe 
title Ash's Tic Tac Toe
echo.

set a[0]= 
set a[1]= 
set a[2]= 
set a[3]= 
set a[4]= 
set a[5]= 
set a[6]= 
set a[7]= 
set a[8]= 
set curr=O
set player1= 
set player2= 
set coord[0]=
set coord[1]=
set gameStatus=0
set count=0

call :setSymbols
call :logDetails
call :flipCurr
call :startGame
goto :eof

:startGame
echo .
call:logCurrentDetails
call :takeCoord
echo %coord[0]% %coord[1]%
call :makeChanges
set /a count=%count%+1
call :viewBoard
call :checkGame
echo GAME STATUS %gameStatus%
echo.
if %gameStatus% EQU 0 (
    call :flipCurr
    call :startGame
) else (
    if %gameStatus% EQU 1 (
        call :winMessage
    )
    if %gameStatus% EQU 2 (
        call :drawMessage
    )
)
goto :eof

:logCurrentDetails
echo %curr%'s Turn
call :viewBoard
goto :eof

:viewBoard
echo   0 1 2
echo 0 %a[0]% %a[1]% %a[2]%
echo 1 %a[3]% %a[4]% %a[5]%
echo 2 %a[6]% %a[7]% %a[8]%
goto :eof

:setSymbols
set /a num=(%RANDOM% %% 2)
if %num% EQU 0 (
    set player1=X 
    set player2=O
) else (
    set player1=O
    set player2=X
    )
goto :eof

:logDetails
echo PLAYER 1 : %player1%
echo PLAYER 2 : %player2%
goto :eof

:takeCoord
set /p "coord[0]=Enter the ordinate of your move:"
set /p "coord[1]=Enter the abscissa of your move:"
goto :eof

:makeChanges
if %coord[0]% EQU 0 (
    if %coord[1]% EQU 0 (
        if "%a[0]%" EQU " " (
            set a[0]=%curr%
        ) else (
            echo The move %coord[0]% %coord[1]% has been played already, try again
            goto :startGame
        )
    )
    if %coord[1]% EQU 1 (
        if "%a[1]%" EQU " " (
            set a[1]=%curr%
        ) else (
            echo The move %coord[0]% %coord[1]% has been played already, try again
            goto :startGame
        )
    )
    if %coord[1]% EQU 2 (
        if "%a[2]%" EQU " " (
            set a[2]=%curr%
        ) else (
            echo The move %coord[0]% %coord[1]% has been played already, try again
            goto :startGame
        )
    )
)
if %coord[0]% EQU 1 (
    if %coord[1]% EQU 0 (
        if "%a[3]%" EQU " " (
            set a[3]=%curr%
        ) else (
            echo The move %coord[0]% %coord[1]% has been played already, try again
            goto :startGame
        )
    )
    if %coord[1]% EQU 1 (
        if "%a[4]%" EQU " " (
            set a[4]=%curr%
        ) else (
            echo The move %coord[0]% %coord[1]% has been played already, try again
            goto :startGame
        )
    )
    if %coord[1]% EQU 2 (
        if "%a[5]%" EQU " " (
            set a[5]=%curr%
        ) else (
            echo The move %coord[0]% %coord[1]% has been played already, try again
            goto :startGame
        )
    )
)
if %coord[0]% EQU 2 (
    if %coord[1]% EQU 0 (
        if "%a[6]%" EQU " " (
            set a[6]=%curr%
        ) else (
            echo The move %coord[0]% %coord[1]% has been played already, try again
            goto :startGame
        )
    )
    if %coord[1]% EQU 1 (
        if "%a[7]%" EQU " " (
            set a[7]=%curr%
        ) else (
            echo The move %coord[0]% %coord[1]% has been played already, try again
            goto :startGame
        )
    )
    if %coord[1]% EQU 2 (
        if "%a[8]%" EQU " " (
            set a[8]=%curr%
        ) else (
            echo The move %coord[0]% %coord[1]% has been played already, try again
            goto :startGame
        )
    )
)
goto :eof

:flipCurr
if %curr% EQU X (
    set curr=O
    color 47
) else (
    set "curr=X"
    color 17
)
goto :eof

:checkGame
if %count% EQU 9 (
    set gameStatus=2
) else (
    if "%a[0]%" NEQ " " (
        if "%a[0]%" EQU "%a[1]%" (
            if "%a[0]%" EQU "%a[2]%" (
                set gameStatus=1
            )   
        )
        if "%a[0]%" EQU "%a[3]%" (
            if "%a[0]%" EQU "%a[6]%" (
                set gameStatus=1
            )
        )
        if "%a[0]%" EQU "%a[4]%" (
            if "%a[0]%" EQU "%a[8]%" (
                set gameStatus=1
            )
        )
    )
    if "%a[1]%" NEQ " " (
        if "%a[1]%" EQU "%a[4]%" (
            if "%a[1]%" EQU "%a[7]%" (
                set gameStatus=1
            )   
        )
    )
    if "%a[2]%" NEQ " " (
        if "%a[2]%" EQU "%a[5]%" (
            if "%a[2]%" EQU "%a[8]%" (
                set gameStatus=1
            )   
        )
        if "%a[2]%" EQU "%a[4]%" (
            if "%a[2]%" EQU "%a[6]%" (
                set gameStatus=1
            )
        )
    )
    if "%a[3]%" NEQ " " (
        if "%a[3]%" EQU "%a[4]%" (
            if "%a[3]%" EQU "%a[5]%" (
                set gameStatus=1
            )   
        )
    )
    if "%a[6]%" NEQ " " (
        if "%a[6]%" EQU "%a[7]%" (
            if "%a[6]%" EQU "%a[8]%" (
                set gameStatus=1
            )   
        )
    )
)
goto :eof

:winMessage
if %player1% EQU %curr% echo PLAYER 1 WON
if %player2% EQU %curr% echo PLAYER 2 WON
goto :eof

:drawMessage
echo It's a draw
goto :eof
