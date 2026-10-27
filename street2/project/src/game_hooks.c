/* Street 2 engine hooks are implemented in native_engine_batch.c and
 * native_command_worker.c, routed by hle/game_hooks.json and CMake.
 * Street 1 frontend addresses must not be transplanted.
 * PC settings: --settings, F1 or Back+Start, or Back where the game's
 * screens show the "PC Settings" hint (hle_options.c).
 */
#include <stdio.h>
#include "recomp/gen/recomp_types.h"

int guest_cpu_native_enter(void);
void guest_cpu_native_leave(int token);

/* Front-end screen loads: 0x1793E0(const char *name) builds "<name>.big"
 * (its "na" check and "%s.big" sit at 0x2D86FC/0x2D8700), the
 * counterpart of Street 1's 0xA2BB0. */
void sub_001793E0_gen(void);
void game_screen_loaded(const char *name);

static void screen_load_hook(void);

void sub_001793E0(void)
{
    int smp = guest_cpu_native_enter();
    screen_load_hook();
    guest_cpu_native_leave(smp);
}

static void screen_load_hook(void)
{
    char name[48];
    uint32_t p = MEM32(g_esp + 4);
    int i;
    for (i = 0; i < 47 && p && MEM8(p + (uint32_t)i); i++)
        name[i] = (char)MEM8(p + (uint32_t)i);
    name[i] = 0;
    sub_001793E0_gen();
    game_screen_loaded(name);
}
