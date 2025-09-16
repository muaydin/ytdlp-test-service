#!/usr/bin/env python3
"""
yt-dlp Service Load Testing Script
Sends concurrent requests to test auto-scaling behavior
"""

import asyncio
import aiohttp
import time
import argparse
import json
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict
import sys

@dataclass
class TestResult:
    url: str
    status: str
    response_time: float
    downloaded_bytes: int
    error: str = ""
    timestamp: str = ""

class YTDLPLoadTester:
    def __init__(self, base_url: str, duration_minutes: int = 5, concurrent_requests: int = 5):
        self.base_url = base_url.rstrip('/')
        self.duration_minutes = duration_minutes
        self.concurrent_requests = concurrent_requests
        self.test_videos = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up
            "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # Me at the zoo (first YouTube video)
            "https://www.youtube.com/watch?v=2NRkV7ZQUJA",  # Charlie bit my finger
            "https://www.youtube.com/watch?v=9bZkp7q19f0",  # PSY - GANGNAM STYLE
            "https://www.youtube.com/watch?v=kJQP7kiw5Fk",  # Luis Fonsi - Despacito
            "https://www.youtube.com/watch?v=fJ9rUzIMcZQ",  # Queen - Bohemian Rhapsody
            "https://www.youtube.com/watch?v=60ItHLz5WEA",  # Alan Walker - Faded
            "https://www.youtube.com/watch?v=hFZFjoX2cGg",  # Ed Sheeran - Shape of You
            "https://www.youtube.com/watch?v=YQHsXMglC9A",  # Adele - Hello
            "https://www.youtube.com/watch?v=pRpeEdMmmQ0",  # Shakira - Waka Waka
            "https://www.youtube.com/watch?v=L_jWHffIx5E",  # Smash Mouth - All Star
            "https://www.youtube.com/watch?v=ZbZSe6N_BXs",  # PPAP (Pen-Pineapple-Apple-Pen)
            "https://www.youtube.com/watch?v=y6120QOlsfU",  # Darude - Sandstorm
            "https://www.youtube.com/watch?v=QH2-TGUlwu4",  # Nyan Cat [original]
            "https://www.youtube.com/watch?v=astISOttCQ0",  # Rebecca Black - Friday
            "https://www.youtube.com/watch?v=RgKAFK5djSk",  # Weezer - Buddy Holly
            "https://www.youtube.com/watch?v=Zi_XLOBDo_Y",  # Billie Jean - Michael Jackson
            "https://www.youtube.com/watch?v=JGw8DWctAts",  # Metallica - Nothing Else Matters
            "https://www.youtube.com/watch?v=rY0WxgSXdEE",  # Nirvana - Smells Like Teen Spirit
            "https://www.youtube.com/watch?v=tbU3zdAgiX8",  # Linkin Park - In the End
            "https://www.youtube.com/watch?v=1w7OgIMMRc4",  # Sweet Child O' Mine - Guns N' Roses
            "https://www.youtube.com/watch?v=QrJSHIys5mM",  # Eminem - Lose Yourself
            "https://www.youtube.com/watch?v=CD-E-LDc384",  # Somebody That I Used to Know - Gotye
            "https://www.youtube.com/watch?v=7PCkvCPvDXk",  # Adele - Rolling in the Deep
            "https://www.youtube.com/watch?v=nrJTHDa7dKY",  # Twenty One Pilots - Stressed Out
            "https://www.youtube.com/watch?v=ru0K8uYEZWw",  # CoComelon - Baby Shark
            "https://www.youtube.com/watch?v=SlPhMPnQ58k",  # Despacito 2 - FlyingKitty
            "https://www.youtube.com/watch?v=sAhEFuq62-I",  # Billie Eilish - bad guy
            "https://www.youtube.com/watch?v=WcO4TPfxPg0",  # The Weeknd - The Hills
            "https://www.youtube.com/watch?v=2vjPBrBU-TM",  # Sia - Chandelier
            "https://www.youtube.com/watch?v=VuNIsY6JdUw",  # Bruno Mars - Just the Way You Are
            "https://www.youtube.com/watch?v=UceaB4D0jpo",  # LMFAO - Party Rock Anthem
            "https://www.youtube.com/watch?v=MrTz5xjmso4",  # Pharrell Williams - Happy
            "https://www.youtube.com/watch?v=5Wiio4KoGe8",  # Gotye - Somebody That I Used to Know
            "https://www.youtube.com/watch?v=Yqo_NUFIz6c",  # Electric Light Orchestra - Mr. Blue Sky
            "https://www.youtube.com/watch?v=djV11Xbc914",  # a-ha - Take On Me
            "https://www.youtube.com/watch?v=dYRs7Q1vfYI",  # The Chainsmokers - Closer
            "https://www.youtube.com/watch?v=TrWOOaFVTVs",  # Meghan Trainor - All About That Bass
            "https://www.youtube.com/watch?v=YqeW9_5kURI",  # Major Lazer - Lean On
            "https://www.youtube.com/watch?v=hT_nvWreIhg",  # OneRepublic - Counting Stars
            "https://www.youtube.com/watch?v=iNzrwh2Z2hQ",  # Maroon 5 - Moves Like Jagger
            "https://www.youtube.com/watch?v=lDK9QqIzhwk",  # Lamb of God - Laid to Rest
            "https://www.youtube.com/watch?v=0J2QdDbelmY",  # Black Sabbath - Paranoid
            "https://www.youtube.com/watch?v=1lyu1KKwC74",  # System of a Down - Toxicity
            "https://www.youtube.com/watch?v=fWNaR-rxAic",  # Cardi B - WAP
            "https://www.youtube.com/watch?v=3tmd-ClpJxA",  # Daft Punk - Get Lucky
            "https://www.youtube.com/watch?v=OPf0YbXqDm0",  # Mark Ronson - Uptown Funk
            "https://www.youtube.com/watch?v=mWRsgZuwf_8",  # Stromae - Alors on Danse
            "https://www.youtube.com/watch?v=gCYcHz2k5x0",  # Icona Pop - I Love It
            "https://www.youtube.com/watch?v=lWA2pjMjpBs",  # David Guetta - Titanium
            "https://www.youtube.com/watch?v=HyHNuVaZJ-k",  # Foster the People - Pumped Up Kicks
            "https://www.youtube.com/watch?v=CevxZvSJLk8",  # Katy Perry - Roar
            "https://www.youtube.com/watch?v=klteYv1Uv9A",  # Fun. - Some Nights
            "https://www.youtube.com/watch?v=pt8VYOfr8To",  # Lorde - Royals
            "https://www.youtube.com/watch?v=6vwNcNOTVzY",  # Ariana Grande - Thank U, Next
            "https://www.youtube.com/watch?v=lczLbpOhvmw",  # Old Town Road - Lil Nas X
            "https://www.youtube.com/watch?v=b6vSf0cA9qY",  # Migos - Bad and Boujee
            "https://www.youtube.com/watch?v=3AtDnEC4zak",  # DJ Khaled - Wild Thoughts
            "https://www.youtube.com/watch?v=iLBBRuVDOo4",  # Kanye West - Stronger
            "https://www.youtube.com/watch?v=Ahha3Cqe_fk",  # DJ Snake - Turn Down for What
            "https://www.youtube.com/watch?v=NUsoVlDFqZg",  # Skrillex - Bangarang
            "https://www.youtube.com/watch?v=YJVmu6yttiw",  # Avicii - Wake Me Up
            "https://www.youtube.com/watch?v=fiore9Z5iUg",  # Swedish House Mafia - Don't You Worry Child
            "https://www.youtube.com/watch?v=uelHwf8o7_U",  # Evanescence - Bring Me to Life
            "https://www.youtube.com/watch?v=JRfuAukYTKg",  # Creed - Higher
            "https://www.youtube.com/watch?v=WM8bTdBs-cw",  # OK Go - Here It Goes Again
            "https://www.youtube.com/watch?v=QcBq-cO_nzU",  # The White Stripes - Seven Nation Army
            "https://www.youtube.com/watch?v=ZrAYw5lMufc",  # The Killers - Mr. Brightside
            "https://www.youtube.com/watch?v=F90Cw4l-8NY",  # The Strokes - Last Nite
            "https://www.youtube.com/watch?v=3MB7T51gOYE",  # Franz Ferdinand - Take Me Out
            "https://www.youtube.com/watch?v=gH476CxJxfg",  # The Kooks - She Moves in Her Own Way
            "https://www.youtube.com/watch?v=6EfhAFA2yFE",  # Arctic Monkeys - 505
            "https://www.youtube.com/watch?v=bpOSxM0rNPM",  # Arctic Monkeys - Do I Wanna Know?
            "https://www.youtube.com/watch?v=TB4xQKJBH4s",  # Foster the People - Sit Next to Me
            "https://www.youtube.com/watch?v=0XFudmaObLI",  # Tame Impala - The Less I Know The Better
            "https://www.youtube.com/watch?v=DiTcxF1iV2c",  # Vampire Weekend - Campus
            "https://www.youtube.com/watch?v=TWcyIpul8OE",  # Glass Animals - Heat Waves
            "https://www.youtube.com/watch?v=myJDBos5Vyw",  # Portugal. The Man - Feel It Still
            "https://www.youtube.com/watch?v=rVqAdIMQZlk",  # Cage the Elephant - Come a Little Closer
            "https://www.youtube.com/watch?v=co7KgV2edvI",  # Jack White - Lazaretto
            "https://www.youtube.com/watch?v=HSN0PgJtIT8",  # Imagine Dragons - Believer
            "https://www.youtube.com/watch?v=I-QfPUz1es8",  # Imagine Dragons - Radioactive
            "https://www.youtube.com/watch?v=sEXHeTcxQy4",  # Panic! At The Disco - High Hopes
            "https://www.youtube.com/watch?v=Pw-0pbY9JeU",  # Fall Out Boy - Sugar, We're Goin Down
            "https://www.youtube.com/watch?v=A9hcJgtnm6Q",  # My Chemical Romance - Welcome to the Black Parade
            "https://www.youtube.com/watch?v=DmeUuoxyt_E",  # All Time Low - Dear Maria, Count Me In
            "https://www.youtube.com/watch?v=N1-xKzPLKAQ",  # Green Day - Boulevard of Broken Dreams
            "https://www.youtube.com/watch?v=JMcNzjzw63I",  # Green Day - American Idiot
            "https://www.youtube.com/watch?v=atxYe-nOa9w",  # Paramore - Still Into You
            "https://www.youtube.com/watch?v=nosKm7zCWfQ",  # Paramore - Misery Business
            "https://www.youtube.com/watch?v=fBYVlFXsEME",  # Twenty One Pilots - Heathens
            "https://www.youtube.com/watch?v=pXRviuL6vMY",  # Twenty One Pilots - Ride
            "https://www.youtube.com/watch?v=92XVwY54h5k",  # Twenty One Pilots - Car Radio
            "https://www.youtube.com/watch?v=WeYsTmIzjkw",  # Linkin Park - Numb
            "https://www.youtube.com/watch?v=eVTXPUF4Oz4",  # Linkin Park - What I've Done
            "https://www.youtube.com/watch?v=kXYiU_JCYtU",  # Linkin Park - Faint
            "https://www.youtube.com/watch?v=7qrRzNidzIc",  # Red Hot Chili Peppers - Dani California
            "https://www.youtube.com/watch?v=YlUKcNNmywk",  # Red Hot Chili Peppers - California Love
            "https://www.youtube.com/watch?v=GLdyP1fYj4o",  # Red Hot Chili Peppers - By the Way
            "https://www.youtube.com/watch?v=k9RyIYrV6EI",  # Foo Fighters - Everlong
            "https://www.youtube.com/watch?v=xQ04WbgI9rg",  # Foo Fighters - Best of You
            "https://www.youtube.com/watch?v=SBjQ9tuuTJQ",  # Foo Fighters - The Pretender
            "https://www.youtube.com/watch?v=QpZHtFO5J3k",  # Pearl Jam - Black
            "https://www.youtube.com/watch?v=4F-inl69C7Q",  # Pearl Jam - Alive
            "https://www.youtube.com/watch?v=7rVlGWyG3A0",  # Pearl Jam - Jeremy
            "https://www.youtube.com/watch?v=OC5J6Q2MqJ8",  # Alice in Chains - Would?
            "https://www.youtube.com/watch?v=CSvFpBOe8eY",  # System of a Down - Chop Suey!
            "https://www.youtube.com/watch?v=rBrQIjh9ig8",  # Tool - Schism
            "https://www.youtube.com/watch?v=oAqKoD6m5m8",  # Radiohead - Creep
            "https://www.youtube.com/watch?v=J69CJ5TW4R8",  # Radiohead - Karma Police
            "https://www.youtube.com/watch?v=VrpGhEVyrk0"   # The Beatles - Come Together
        ]
        self.results: List[TestResult] = []
        self.start_time = None
        self.end_time = None
        
    async def send_download_request(self, session: aiohttp.ClientSession, video_url: str, request_id: int) -> TestResult:
        """Send a single download request and return the result"""
        start_time = time.time()
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        try:
            payload = {"url": video_url}
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            timeout = aiohttp.ClientTimeout(total=60)  # 60 second timeout
            
            async with session.post(
                f"{self.base_url}/test-download",
                json=payload,
                headers=headers,
                timeout=timeout
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success', False):
                        return TestResult(
                            url=video_url,
                            status="SUCCESS",
                            response_time=response_time,
                            downloaded_bytes=data.get('downloaded_bytes', 0),
                            timestamp=timestamp
                        )
                    else:
                        return TestResult(
                            url=video_url,
                            status="FAILED",
                            response_time=response_time,
                            downloaded_bytes=0,
                            error=data.get('error', 'Unknown error'),
                            timestamp=timestamp
                        )
                else:
                    return TestResult(
                        url=video_url,
                        status="HTTP_ERROR",
                        response_time=response_time,
                        downloaded_bytes=0,
                        error=f"HTTP {response.status}",
                        timestamp=timestamp
                    )
                    
        except asyncio.TimeoutError:
            return TestResult(
                url=video_url,
                status="TIMEOUT",
                response_time=time.time() - start_time,
                downloaded_bytes=0,
                error="Request timeout after 60s",
                timestamp=timestamp
            )
        except Exception as e:
            return TestResult(
                url=video_url,
                status="ERROR",
                response_time=time.time() - start_time,
                downloaded_bytes=0,
                error=str(e),
                timestamp=timestamp
            )

    def get_next_video_url(self, request_count: int) -> str:
        """Get the next video URL in rotation"""
        return self.test_videos[request_count % len(self.test_videos)]

    def print_result(self, result: TestResult, request_id: int):
        """Print a single test result with clean formatting"""
        status_color = {
            "SUCCESS": "\033[92m",  # Green
            "FAILED": "\033[91m",   # Red
            "TIMEOUT": "\033[93m",  # Yellow
            "ERROR": "\033[91m",    # Red
            "HTTP_ERROR": "\033[91m"  # Red
        }
        reset_color = "\033[0m"
        
        color = status_color.get(result.status, "")
        status_icon = "✅" if result.status == "SUCCESS" else "❌"
        
        # Extract video title from URL for cleaner display
        video_id = result.url.split('=')[-1][:11] if '=' in result.url else "unknown"
        
        if result.status == "SUCCESS":
            size_mb = result.downloaded_bytes / (1024 * 1024)
            print(f"{status_icon} [{result.timestamp}] Req#{request_id:3d} | {color}{result.status:10s}{reset_color} | "
                  f"{video_id} | {result.response_time:6.2f}s | {size_mb:6.2f}MB")
        else:
            print(f"{status_icon} [{result.timestamp}] Req#{request_id:3d} | {color}{result.status:10s}{reset_color} | "
                  f"{video_id} | {result.response_time:6.2f}s | {result.error}")

    def print_progress(self, completed: int, total_time: float):
        """Print progress update"""
        elapsed_minutes = total_time / 60
        remaining_minutes = max(0, self.duration_minutes - elapsed_minutes)
        print(f"\n📊 Progress: {completed} requests completed | "
              f"⏱️  Elapsed: {elapsed_minutes:.1f}m | Remaining: {remaining_minutes:.1f}m")

    def print_summary(self):
        """Print final test summary"""
        if not self.results:
            print("\n❌ No results to summarize")
            return
            
        total_requests = len(self.results)
        successful = sum(1 for r in self.results if r.status == "SUCCESS")
        failed = total_requests - successful
        
        total_bytes = sum(r.downloaded_bytes for r in self.results if r.status == "SUCCESS")
        total_mb = total_bytes / (1024 * 1024)
        
        avg_response_time = sum(r.response_time for r in self.results) / total_requests
        
        success_rate = (successful / total_requests) * 100
        
        total_duration = (self.end_time - self.start_time).total_seconds()
        requests_per_minute = (total_requests / total_duration) * 60
        
        print(f"\n{'='*80}")
        print(f"🎯 LOAD TEST SUMMARY")
        print(f"{'='*80}")
        print(f"⏱️  Duration: {total_duration/60:.1f} minutes")
        print(f"📈 Total Requests: {total_requests}")
        print(f"✅ Successful: {successful} ({success_rate:.1f}%)")
        print(f"❌ Failed: {failed} ({100-success_rate:.1f}%)")
        print(f"⚡ Avg Response Time: {avg_response_time:.2f}s")
        print(f"📊 Requests/min: {requests_per_minute:.1f}")
        print(f"💾 Total Downloaded: {total_mb:.2f} MB")
        
        # Failure breakdown
        if failed > 0:
            print(f"\n❌ Failure Breakdown:")
            failure_types = {}
            for result in self.results:
                if result.status != "SUCCESS":
                    failure_types[result.status] = failure_types.get(result.status, 0) + 1
            
            for failure_type, count in failure_types.items():
                print(f"   {failure_type}: {count}")
        
        print(f"{'='*80}")

    async def run_load_test(self):
        """Run the load test"""
        print(f"🚀 Starting yt-dlp Load Test")
        print(f"🎯 Target: {self.base_url}")
        print(f"⏱️  Duration: {self.duration_minutes} minutes")
        print(f"🔄 Concurrent Requests: {self.concurrent_requests}")
        print(f"🎬 Video Pool: {len(self.test_videos)} videos")
        print(f"{'='*80}")
        print(f"{'Status':<12} | {'Video ID':<11} | {'Time':<8} | {'Size/Error'}")
        print(f"{'='*80}")
        
        self.start_time = datetime.now()
        end_time = self.start_time + timedelta(minutes=self.duration_minutes)
        
        request_count = 0
        
        async with aiohttp.ClientSession() as session:
            while datetime.now() < end_time:
                # Create batch of concurrent requests
                tasks = []
                batch_start_count = request_count
                
                for i in range(self.concurrent_requests):
                    if datetime.now() >= end_time:
                        break
                        
                    video_url = self.get_next_video_url(request_count)
                    task = self.send_download_request(session, video_url, request_count + 1)
                    tasks.append(task)
                    request_count += 1
                
                if not tasks:
                    break
                
                # Wait for all requests in this batch to complete
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process and display results
                for i, result in enumerate(results):
                    if isinstance(result, TestResult):
                        self.results.append(result)
                        self.print_result(result, batch_start_count + i + 1)
                    else:
                        # Handle exceptions
                        error_result = TestResult(
                            url="unknown",
                            status="EXCEPTION",
                            response_time=0,
                            downloaded_bytes=0,
                            error=str(result),
                            timestamp=datetime.now().strftime("%H:%M:%S")
                        )
                        self.results.append(error_result)
                        self.print_result(error_result, batch_start_count + i + 1)
                
                # Print progress every 10 requests
                if len(self.results) % 10 == 0:
                    elapsed_time = (datetime.now() - self.start_time).total_seconds()
                    self.print_progress(len(self.results), elapsed_time)
                
                # Small delay between batches to avoid overwhelming the service
                await asyncio.sleep(2)
        
        self.end_time = datetime.now()
        self.print_summary()

async def main():
    parser = argparse.ArgumentParser(description="yt-dlp Service Load Tester")
    parser.add_argument("--url", default="http://51.159.205.195", 
                       help="Base URL of yt-dlp service (default: http://51.159.205.195)")
    parser.add_argument("--duration", type=int, default=5,
                       help="Test duration in minutes (default: 5)")
    parser.add_argument("--concurrent", type=int, default=5,
                       help="Number of concurrent requests (default: 5)")
    
    args = parser.parse_args()
    
    # Test connection first
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{args.url}/health", timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    print(f"❌ Service health check failed: HTTP {response.status}")
                    return 1
    except Exception as e:
        print(f"❌ Cannot connect to service at {args.url}: {e}")
        return 1
    
    print(f"✅ Service health check passed")
    
    tester = YTDLPLoadTester(args.url, args.duration, args.concurrent)
    await tester.run_load_test()
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(130) 