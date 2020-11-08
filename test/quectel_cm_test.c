#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

/**
 * Silly test that just lets us simulate Quectel_CM working without a real modem.
 * gcc quectel_cm_test.c -o quectel_CM
 */
int main()
{
    time_t t = time(NULL);
    struct tm tm = *localtime(&t);

    while (1) {
        t = time(NULL);
        tm = *gmtime(&t);
        printf("[%02d-%02d_%02d:%02d:%02d:000] ",tm.tm_mon + 1, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec);
        printf("requestRegistrationState2 MCC: 234, MNC: 20, PS: Attached, DataCap: LTE\n");
        fflush(stdout);
        sleep(5);  
    }

    return 0;
}
