/*
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#ifdef _WIN32
    #include <windows.h> // For Sleep on Windows
    #define sleep_ms(ms) Sleep(ms)
#else
    #include <unistd.h> // For usleep on Unix-like systems
    #define sleep_ms(ms) usleep((ms) * 1000)
#endif

// Function to generate a random hex key (128 bits = 32 hex chars)
void generate_key(char *key) {
    for (int i = 0; i < 32; i++) {
        int nibble = rand() % 16;
        key[i] = nibble < 10 ? '0' + nibble : 'a' + (nibble - 10);
    }
    key[32] = '\0';
}

int main() {
    // Seed the random number generator
    srand((unsigned int)time(NULL));

    char key[33]; // 32 hex chars + null terminator

    while (1) {
        // 1. Timestamp for SPD1 and SPD2 histograms (0 to 9999)
        int timestamp = rand() % 10000;
        printf("TIMESTAMP,%d\n", timestamp);
        fflush(stdout);

        // 2. QBER (0.0 to 10.0)
        float qber = (float)(rand() % 1000) / 100.0; // 0.00 to 9.99
        printf("QBER,%.2f\n", qber);
        fflush(stdout);

        // 3. Throughput (kbps) - Random (0.0 to 10.0)
        float kbps = (float)(rand() % 1000) / 100.0; // 0.00 to 9.99
        printf("KBPS,%.2f\n", kbps);
        fflush(stdout);

        // 4. Visibility (0.0 to 1.0)
        float visibility = (float)(rand() % 100) / 100.0; // 0.00 to 0.99
        printf("VISIBILITY,%.2f\n", visibility);
        fflush(stdout);

        // 5. SPD1 Decoy Randomness (0.0 to 10.0)
        float spd1_decay = (float)(rand() % 1000) / 100.0; // 0.00 to 9.99
        printf("SPD1_DECAYSTATE,%.2f\n", spd1_decay);
        fflush(stdout);

        // 6. Key (128-bit as 32 hex chars)
        generate_key(key);
        printf("KEY,0x%s\n", key);
        fflush(stdout);

        // Sleep for 100ms after generating data
        sleep_ms(100);

        // Sleep for 10ms (queue clearing will be handled in Python)
        sleep_ms(10);
    }

    return 0;
}
    */



#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h> // For strlen if needed, though not strictly in this version

#ifdef _WIN32
    #include <windows.h> // For Sleep on Windows
    #define sleep_ms(ms) Sleep(ms)
#else
    #include <unistd.h> // For usleep on Unix-like systems
    #define sleep_ms(ms) usleep((ms) * 1000)
#endif

// Function to generate a random 128-bit key as a binary string (128 chars of '0' or '1')
void generate_key(char *key) {
    for (int i = 0; i < 128; i++) { // For a 128-bit key
        key[i] = (rand() % 2) == 0 ? '0' : '1'; // Generate '0' or '1'
    }
    key[128] = '\0'; // Null-terminate the string
}

int main() {
    // Seed the random number generator
    srand((unsigned int)time(NULL));

    char key[129]; // 128 binary chars + null terminator
    int session_number = 0;

    while (1) {
        printf("SESSION_NUMBER:%d\n", session_number++);
        fflush(stdout);

        // Generate SPD1 values
        printf("SPD1_VALUES:\n");
        for (int i = 0; i < 40; i++) {
            int timestamp_spd1 = rand() % 10000;
            printf("%d\n", timestamp_spd1);
            fflush(stdout);
            
        }

        // SPD1 Decoy Randomness (0.0 to 1.0)
        float spd1_decoy_randomness = (float)(rand() % 10000) / 10000.0; // 0.0000 to 0.9999
        printf("DECOY_STATE_RANDOMNESS_AT_SPD1:%.4f\n", spd1_decoy_randomness);
        fflush(stdout);

        // Generate SPD2 values
        printf("SPD2_VALUES:\n");
        for (int i = 0; i < 40; i++) {
            int timestamp_spd2 = rand() % 10000;
            printf("%d\n", timestamp_spd2);
            fflush(stdout);
            
        }

        // Visibility (0.0 to 1.0)
        float visibility = (float)(rand() % 10000) / 10000.0; // 0.0000 to 0.9999
        printf("VISIBILITY_RATIO_IS:%.4f\n", visibility);
        fflush(stdout);

        // QBER (0.0 to 10.0)
        float qber = (float)(rand() % 1000) / 100.0; // 0.00 to 9.99
        printf("SPD1_QBER_VALUE_IS:%.2f\n", qber);
        fflush(stdout);

        // Generate the 128-bit key
        if(session_number%2==0)
        {
            generate_key(key);
            printf("NUMBER_OF_RX_KEY_BITS_AFTER_PRIVACY_AMPLIFICATION_IS:%d\n", 128);
            printf("KEY_BITS:%s\n", key);
            fflush(stdout);
        }

        // Throughput (kbps) - Random (0.0 to 10.0)
        if(session_number%2==1)
        {
            float kbps = (float)(rand() % 1000) / 100.0; // 0.00 to 9.99
            printf("KEY_RATE_PER_SECOND_IS:%.2f\n", kbps);
            fflush(stdout);
        }



        printf("\n");

        

        // Sleep for 10ms before the next session
        //sleep_ms(10);
    }

    return 0;
}