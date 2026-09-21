#include <stdio.h>
#include <stdint.h>
typedef uint64_t u64; typedef uint16_t u16;
static const int SB[16]={1,10,4,12,6,15,3,9,2,13,11,7,5,0,8,14};
static int P[64]; static int RC[28];
static u16 rl(u16 x,int s){s&=15;return s?(u16)((x<<s)|(x>>(16-s))):x;}
static u64 T(u64 s){u64 t=0;for(int j=0;j<16;j++)t|=(u64)SB[(s>>(4*j))&15]<<(4*j);
 u16 a=t>>48,b=t>>32,c=t>>16,d=t; a=rl(a,1);b=rl(b,4);c=rl(c,7);d=rl(d,11);a=a+b;c=c+d;
 u64 m=((u64)a<<48)|((u64)b<<32)|((u64)c<<16)|d; u64 o=0; for(int i=0;i<64;i++) if((m>>i)&1) o|=1ULL<<P[i]; return o;}
int perm6[720][6]; int np=0;
void gen(int *a,int k){ if(k==6){for(int i=0;i<6;i++)perm6[np][i]=a[i];np++;return;} for(int i=k;i<6;i++){int t=a[k];a[k]=a[i];a[i]=t;gen(a,k+1);t=a[k];a[k]=a[i];a[i]=t;}}
int main(){
  for(int i=0;i<64;i++)P[i]=4*(i/16)+16*((3*((i%16)/4)+(i%4))%4)+(i%4);
  int l=1; for(int r=0;r<28;r++){RC[r]=l;int b=((l>>4)^(l>>1))&1; l=((l<<1)|b)&31;}
  int a[6]={0,1,2,3,4,5}; gen(a,0);
  long hits=0;
  for(int pi=0;pi<720;pi++) for(int s12=0;s12<6;s12++) for(int s2=0;s2<6;s2++){ if(s12==s2) continue;
   for(int rd=0;rd<2;rd++) for(int sm=0;sm<64;sm++){int pc=__builtin_popcount(sm); if(pc<3||pc>4) continue;
    for(int rci=0;rci<6;rci++) for(int sh=0;sh<=32;sh+=16){
      u16 w[6]={0}; u64 s=0;
      for(int r=0;r<28;r++){
        u64 rk=0; for(int q=0;q<4;q++) rk|=(u64)w[sh/16+q]<<(16*q);
        s=T(s^rk); u16 n[6];
        for(int i=0;i<6;i++){int src=perm6[pi][i]; u16 x=w[src];
          if(src==s12) x=rl(x, rd?12:4); if(src==s2) x=rl(x, rd?2:14); n[i]=x;}
        for(int i=0;i<6;i++) if(sm>>i&1) n[i]=(u16)((SB[n[i]>>12]<<12)|(n[i]&0xfff));
        n[rci]^=RC[r]; for(int i=0;i<6;i++)w[i]=n[i];}
      if(s==0xD873355EC63B1B4BULL){hits++; printf("hit pi=%d s12=%d s2=%d rd=%d sm=%x rci=%d sh=%d\n",pi,s12,s2,rd,sm,rci,sh);}
  }}}
  printf("hits %ld\n",hits);}
