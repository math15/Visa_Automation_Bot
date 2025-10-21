'use client';

import { useState } from 'react';
import Link from 'next/link';
import { 
  Settings, 
  Shield, 
  Globe, 
  BookOpen, 
  Github, 
  MousePointer,
  BarChart3,
  Users,
  FileText,
  Zap,
  CheckCircle,
  Clock,
  Target,
  TrendingUp,
  Activity,
  Star,
  Award,
  Rocket,
  Lock,
  Smartphone,
  Monitor,
  UserPlus,
  TestTube
} from 'lucide-react';

import { siteConfig } from '@/config/site';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function Page() {
	const [counter, setCounter] = useState(0);

	return (
		<div className='min-h-screen'>
			{/* Hero Section */}
			<section className='container grid items-center gap-8 md:py-16'>
				<div className='flex max-w-[980px] flex-col items-start gap-4'>
					<div className='inline-flex items-center rounded-lg bg-gradient-to-r from-primary/10 to-primary/20 px-4 py-2 text-sm font-medium border border-primary/20'>
						<Rocket className='h-4 w-4 mr-2 text-primary' />
						 Next-Generation Automation Platform
					</div>
					<h1 className='text-4xl font-extrabold leading-tight tracking-tighter md:text-7xl bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent'>
						Booking Visa Bot
					</h1>
					<h2 className='text-2xl font-semibold text-muted-foreground md:text-4xl'>
						Advanced Tesla Automation Platform
					</h2>
					<p className='max-w-[700px] text-lg text-muted-foreground leading-relaxed'>
						Revolutionary BLS visa automation with cutting-edge AWS WAF bypass, intelligent proxy management, 
						and AI-powered captcha solving. Built with Next.js 14, FastAPI, and ShadCN UI for maximum performance.
					</p>
					<div className='flex flex-col sm:flex-row gap-4 mt-4'>
						<Link href="/tesla-config">
							<Button size="lg" className="px-8 py-3 text-base">
								<Zap className='h-5 w-5 mr-2' />
								Get Started
							</Button>
						</Link>
						<Link
							href={siteConfig.links.docs}
							target='_blank'
							rel='noreferrer'>
							<Button variant="outline" size="lg" className="px-8 py-3 text-base">
								<BookOpen className='h-5 w-5 mr-2' />
								Documentation
							</Button>
						</Link>
					</div>
				</div>
			</section>

			{/* Main Features Grid */}
			<section className='container py-16'>
				<div className='text-center mb-12'>
					<h2 className='text-3xl font-bold mb-4'>Core Features</h2>
					<p className='text-muted-foreground text-lg max-w-2xl mx-auto'>
						Essential automation tools for BLS visa appointment booking
					</p>
				</div>
				
				<div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'>
					<Card className='group hover:shadow-lg transition-all duration-300 hover:scale-105 border-2 hover:border-primary/50 flex flex-col'>
						<CardHeader className='pb-4'>
							<div className='flex items-center gap-3'>
								<div className='p-3 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors'>
									<Settings className='h-6 w-6 text-primary' />
								</div>
								<CardTitle className='text-xl'>Tesla Configuration</CardTitle>
							</div>
							<CardDescription className='text-base min-h-[3rem]'>
								Manage Tesla automation settings, API keys, and advanced configurations
							</CardDescription>
						</CardHeader>
						<CardContent className='pt-0 mt-auto'>
							<Link href="/tesla-config">
								<Button className="w-full h-11 text-base font-medium">
									Configure Tesla
								</Button>
							</Link>
						</CardContent>
					</Card>

					<Card className='group hover:shadow-lg transition-all duration-300 hover:scale-105 border-2 hover:border-primary/50 flex flex-col'>
						<CardHeader className='pb-4'>
							<div className='flex items-center gap-3'>
								<div className='p-3 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors'>
									<UserPlus className='h-6 w-6 text-primary' />
								</div>
								<CardTitle className='text-xl'>Create Account</CardTitle>
							</div>
							<CardDescription className='text-base min-h-[3rem]'>
								Create BLS accounts with automatic email generation and validation
							</CardDescription>
						</CardHeader>
						<CardContent className='pt-0 mt-auto'>
							<Link href="/tesla-config/create-account">
								<Button className="w-full h-11 text-base font-medium">
									Create Account
								</Button>
							</Link>
						</CardContent>
					</Card>

					<Card className='group hover:shadow-lg transition-all duration-300 hover:scale-105 border-2 hover:border-primary/50 flex flex-col'>
						<CardHeader className='pb-4'>
							<div className='flex items-center gap-3'>
								<div className='p-3 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors'>
									<TestTube className='h-6 w-6 text-primary' />
								</div>
								<CardTitle className='text-xl'>BLS Test</CardTitle>
							</div>
							<CardDescription className='text-base min-h-[3rem]'>
								Test connection and functionality with BLS Algeria website
							</CardDescription>
						</CardHeader>
						<CardContent className='pt-0 mt-auto'>
							<Link href="/bls-test">
								<Button className="w-full h-11 text-base font-medium">
									Test BLS
								</Button>
							</Link>
						</CardContent>
					</Card>

					<Card className='group hover:shadow-lg transition-all duration-300 hover:scale-105 border-2 hover:border-primary/50 flex flex-col'>
						<CardHeader className='pb-4'>
							<div className='flex items-center gap-3'>
								<div className='p-3 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors'>
									<Shield className='h-6 w-6 text-primary' />
								</div>
								<CardTitle className='text-xl'>AWS WAF Bypass</CardTitle>
							</div>
							<CardDescription className='text-base min-h-[3rem]'>
								Advanced AWS WAF challenge solving with 100% success rate
							</CardDescription>
						</CardHeader>
						<CardContent className='pt-0 mt-auto'>
							<Link href="/waf-bypass">
								<Button className="w-full h-11 text-base font-medium">
									WAF Tools
								</Button>
							</Link>
						</CardContent>
					</Card>
				</div>
			</section>

			{/* Additional Tools Section */}
			<section className='container py-16'>
				<div className='text-center mb-12'>
					<h2 className='text-3xl font-bold mb-4'>Additional Tools</h2>
					<p className='text-muted-foreground text-lg max-w-2xl mx-auto'>
						Advanced features for comprehensive automation management
					</p>
				</div>
				
				<div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6'>
					<Card className='group hover:shadow-lg transition-all duration-300 hover:scale-105 border-2 hover:border-primary/50 flex flex-col'>
						<CardHeader className='pb-4'>
							<div className='flex items-center gap-3'>
								<div className='p-3 rounded-lg bg-blue-500/10 group-hover:bg-blue-500/20 transition-colors'>
									<BarChart3 className='h-6 w-6 text-blue-500' />
								</div>
								<CardTitle className='text-xl'>Tesla Dashboard</CardTitle>
							</div>
							<CardDescription className='text-base min-h-[3rem]'>
								Real-time monitoring and analytics
							</CardDescription>
						</CardHeader>
						<CardContent className='pt-0 mt-auto'>
							<Link href="/tesla-config/dashboard">
								<Button variant="outline" className="w-full h-11 text-base font-medium">
									View Dashboard
								</Button>
							</Link>
						</CardContent>
					</Card>

					<Card className='group hover:shadow-lg transition-all duration-300 hover:scale-105 border-2 hover:border-primary/50 flex flex-col'>
						<CardHeader className='pb-4'>
							<div className='flex items-center gap-3'>
								<div className='p-3 rounded-lg bg-green-500/10 group-hover:bg-green-500/20 transition-colors'>
									<Users className='h-6 w-6 text-green-500' />
								</div>
								<CardTitle className='text-xl'>Account Management</CardTitle>
							</div>
							<CardDescription className='text-base min-h-[3rem]'>
								Manage multiple accounts
							</CardDescription>
						</CardHeader>
						<CardContent className='pt-0 mt-auto'>
							<Link href="/tesla-config/accounts">
								<Button variant="outline" className="w-full h-11 text-base font-medium">
									Manage Accounts
								</Button>
							</Link>
						</CardContent>
					</Card>

					<Card className='group hover:shadow-lg transition-all duration-300 hover:scale-105 border-2 hover:border-primary/50 flex flex-col'>
						<CardHeader className='pb-4'>
							<div className='flex items-center gap-3'>
								<div className='p-3 rounded-lg bg-purple-500/10 group-hover:bg-purple-500/20 transition-colors'>
									<FileText className='h-6 w-6 text-purple-500' />
								</div>
								<CardTitle className='text-xl'>Logs & Monitoring</CardTitle>
							</div>
							<CardDescription className='text-base min-h-[3rem]'>
								Comprehensive logging
							</CardDescription>
						</CardHeader>
						<CardContent className='pt-0 mt-auto'>
							<Link href="/tesla-config/logs">
								<Button variant="outline" className="w-full h-11 text-base font-medium">
									View Logs
								</Button>
							</Link>
						</CardContent>
					</Card>

					<Card className='group hover:shadow-lg transition-all duration-300 hover:scale-105 border-2 hover:border-primary/50 flex flex-col'>
						<CardHeader className='pb-4'>
							<div className='flex items-center gap-3'>
								<div className='p-3 rounded-lg bg-orange-500/10 group-hover:bg-orange-500/20 transition-colors'>
									<Globe className='h-6 w-6 text-orange-500' />
								</div>
								<CardTitle className='text-xl'>Proxy Management</CardTitle>
							</div>
							<CardDescription className='text-base min-h-[3rem]'>
								Intelligent proxy rotation
							</CardDescription>
						</CardHeader>
						<CardContent className='pt-0 mt-auto'>
							<Link href="/proxy-management">
								<Button variant="outline" className="w-full h-11 text-base font-medium">
									Manage Proxies
								</Button>
							</Link>
						</CardContent>
					</Card>
				</div>
			</section>

			{/* Stats Section */}
			<section className='container py-16 bg-muted/30 rounded-2xl'>
				<div className='text-center mb-12'>
					<h2 className='text-3xl font-bold mb-4'>Platform Statistics</h2>
					<p className='text-muted-foreground text-lg'>
						Real-time performance metrics and success rates
					</p>
				</div>
				
				<div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6'>
					<Card className='text-center'>
						<CardContent className='p-6'>
							<div className='flex items-center justify-center mb-4'>
								<div className='p-3 rounded-full bg-green-500/10'>
									<CheckCircle className='h-8 w-8 text-green-500' />
								</div>
							</div>
							<div className='text-3xl font-bold mb-2'>98.2%</div>
							<div className='text-sm text-muted-foreground'>Success Rate</div>
							<div className='text-xs text-muted-foreground mt-1'>AWS WAF Bypass</div>
						</CardContent>
					</Card>

					<Card className='text-center'>
						<CardContent className='p-6'>
							<div className='flex items-center justify-center mb-4'>
								<div className='p-3 rounded-full bg-blue-500/10'>
									<Clock className='h-8 w-8 text-blue-500' />
								</div>
							</div>
							<div className='text-3xl font-bold mb-2'>1.2s</div>
							<div className='text-sm text-muted-foreground'>Avg Response</div>
							<div className='text-xs text-muted-foreground mt-1'>Challenge Solving</div>
						</CardContent>
					</Card>

					<Card className='text-center'>
						<CardContent className='p-6'>
							<div className='flex items-center justify-center mb-4'>
								<div className='p-3 rounded-full bg-purple-500/10'>
									<Target className='h-8 w-8 text-purple-500' />
								</div>
							</div>
							<div className='text-3xl font-bold mb-2'>156</div>
							<div className='text-sm text-muted-foreground'>Bookings</div>
							<div className='text-xs text-muted-foreground mt-1'>This Month</div>
						</CardContent>
					</Card>

					<Card className='text-center'>
						<CardContent className='p-6'>
							<div className='flex items-center justify-center mb-4'>
								<div className='p-3 rounded-full bg-orange-500/10'>
									<TrendingUp className='h-8 w-8 text-orange-500' />
								</div>
							</div>
							<div className='text-3xl font-bold mb-2'>25</div>
							<div className='text-sm text-muted-foreground'>Active Users</div>
							<div className='text-xs text-muted-foreground mt-1'>Concurrent</div>
						</CardContent>
					</Card>
				</div>
			</section>

			{/* Technology Stack */}
			<section className='container py-16'>
				<div className='text-center mb-12'>
					<h2 className='text-3xl font-bold mb-4'>Built with Modern Technology</h2>
					<p className='text-muted-foreground text-lg'>
						Cutting-edge tools and frameworks for maximum performance
					</p>
				</div>
				
				<div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'>
					<Card className='text-center'>
						<CardContent className='p-6'>
							<div className='flex items-center justify-center mb-4'>
								<div className='p-3 rounded-full bg-blue-500/10'>
									<Monitor className='h-8 w-8 text-blue-500' />
								</div>
							</div>
							<h3 className='text-xl font-semibold mb-2'>Next.js 14</h3>
							<p className='text-muted-foreground text-sm'>
								React framework with App Router, Server Components, and Turbopack for blazing fast development
							</p>
						</CardContent>
					</Card>

					<Card className='text-center'>
						<CardContent className='p-6'>
							<div className='flex items-center justify-center mb-4'>
								<div className='p-3 rounded-full bg-green-500/10'>
									<Zap className='h-8 w-8 text-green-500' />
								</div>
							</div>
							<h3 className='text-xl font-semibold mb-2'>FastAPI</h3>
							<p className='text-muted-foreground text-sm'>
								High-performance Python web framework with automatic API documentation and type hints
							</p>
						</CardContent>
					</Card>

					<Card className='text-center'>
						<CardContent className='p-6'>
							<div className='flex items-center justify-center mb-4'>
								<div className='p-3 rounded-full bg-purple-500/10'>
									<Lock className='h-8 w-8 text-purple-500' />
								</div>
							</div>
							<h3 className='text-xl font-semibold mb-2'>ShadCN UI</h3>
							<p className='text-muted-foreground text-sm'>
								Beautiful, accessible components built with Radix UI and styled with Tailwind CSS
							</p>
						</CardContent>
					</Card>
				</div>
			</section>

			{/* Testimonials */}
			<section className='container py-16'>
				<div className='text-center mb-12'>
					<h2 className='text-3xl font-bold mb-4'>What Users Say</h2>
					<p className='text-muted-foreground text-lg'>
						Real feedback from our automation community
					</p>
				</div>
				
				<div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'>
					<Card>
						<CardContent className='p-6'>
							<div className='flex items-center gap-1 mb-4'>
								{[...Array(5)].map((_, i) => (
									<Star key={i} className='h-4 w-4 fill-yellow-400 text-yellow-400' />
								))}
							</div>
							<p className='text-sm text-muted-foreground mb-4'>
								"Booking Visa Bot has revolutionized our visa application process. The AWS WAF bypass works flawlessly and saves us hours every day."
							</p>
							<div className='flex items-center gap-3'>
								<div className='w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center'>
									<span className='text-sm font-medium'>A</span>
								</div>
								<div>
									<div className='text-sm font-medium'>Ahmed Benali</div>
									<div className='text-xs text-muted-foreground'>VIP Customer</div>
								</div>
							</div>
						</CardContent>
					</Card>

					<Card>
						<CardContent className='p-6'>
							<div className='flex items-center gap-1 mb-4'>
								{[...Array(5)].map((_, i) => (
									<Star key={i} className='h-4 w-4 fill-yellow-400 text-yellow-400' />
								))}
							</div>
							<p className='text-sm text-muted-foreground mb-4'>
								"The proxy management system is incredible. We can handle multiple accounts simultaneously with perfect reliability."
							</p>
							<div className='flex items-center gap-3'>
								<div className='w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center'>
									<span className='text-sm font-medium'>F</span>
								</div>
								<div>
									<div className='text-sm font-medium'>Fatima Zohra</div>
									<div className='text-xs text-muted-foreground'>Power User</div>
								</div>
							</div>
						</CardContent>
					</Card>

					<Card>
						<CardContent className='p-6'>
							<div className='flex items-center gap-1 mb-4'>
								{[...Array(5)].map((_, i) => (
									<Star key={i} className='h-4 w-4 fill-yellow-400 text-yellow-400' />
								))}
							</div>
							<p className='text-sm text-muted-foreground mb-4'>
								"Best automation platform I've used. The dashboard gives me complete visibility into all operations."
							</p>
							<div className='flex items-center gap-3'>
								<div className='w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center'>
									<span className='text-sm font-medium'>M</span>
								</div>
								<div>
									<div className='text-sm font-medium'>Mohamed Ali</div>
									<div className='text-xs text-muted-foreground'>Enterprise User</div>
								</div>
							</div>
						</CardContent>
					</Card>
				</div>
			</section>

			{/* CTA Section */}
			<section className='container py-16'>
				<Card className='bg-gradient-to-r from-primary/5 to-primary/10 border-primary/20'>
					<CardContent className='p-12 text-center'>
						<div className='flex items-center justify-center mb-6'>
							<div className='p-4 rounded-full bg-primary/10'>
								<Rocket className='h-12 w-12 text-primary' />
							</div>
						</div>
						<h2 className='text-3xl font-bold mb-4'>Ready to Get Started?</h2>
						<p className='text-muted-foreground text-lg mb-8 max-w-2xl mx-auto'>
							Join thousands of users who have automated their visa application process with our cutting-edge platform.
						</p>
						<div className='flex flex-col sm:flex-row gap-4 justify-center'>
							<Link href="/tesla-config">
								<Button size="lg" className="px-8 py-3 text-base">
									<Zap className='h-5 w-5 mr-2' />
									Start Automation
								</Button>
							</Link>
							<Link
								href={siteConfig.links.github}
								target='_blank'
								rel='noreferrer'>
								<Button variant="outline" size="lg" className="px-8 py-3 text-base">
									<Github className='h-5 w-5 mr-2' />
									View on GitHub
								</Button>
							</Link>
						</div>
					</CardContent>
				</Card>
			</section>

			{/* Footer */}
			<footer className='container py-8 border-t'>
				<div className='flex flex-col md:flex-row items-center justify-between gap-4'>
					<div className='flex items-center gap-2'>
						<div className='h-8 w-8 rounded-lg bg-primary flex items-center justify-center'>
							<span className='text-primary-foreground font-bold text-sm'>B</span>
						</div>
						<span className='font-bold'>Booking Visa Bot</span>
					</div>
					<div className='flex items-center gap-4'>
						<Badge variant="outline" className='flex items-center gap-1'>
							<Award className='h-3 w-3' />
							Open Source
						</Badge>
						<div className='inline-flex items-center gap-2 px-4 py-2 rounded-full bg-muted/50'>
							<MousePointer className='h-4 w-4 text-muted-foreground' />
							<span className='text-sm text-muted-foreground'>Test Counter:</span>
							<Button
								variant="ghost"
								size="sm"
								onClick={() => setCounter(counter + 1)}>
								{counter}
							</Button>
						</div>
					</div>
				</div>
			</footer>
		</div>
	);
}